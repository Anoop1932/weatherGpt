import logging
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.ai.nlp_parser import nlp_parser, KNOWN_CITIES
from app.ai.grounded_llm import grounded_llm_engine, clean_svg_and_markup
from app.weather.orchestrator import weather_orchestrator
from app.weather.ranking import get_regional_ranking
from app.risk.engine import risk_engine
from app.utils.geocoding import geocode_location
from app.schemas.weather_schemas import WeatherQueryRequest, WeatherQueryResponse, RiskEvaluation
from app.models.db_models import WeatherQuery

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["AI Conversational Intelligence"])


@router.post("/query", response_model=WeatherQueryResponse)
async def process_weather_query(
    req: WeatherQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Resolve conversation context from req.conversation_context if last_location not explicitly given
        last_loc = req.last_location
        last_dt = req.last_date
        last_it = req.last_intent

        if not last_loc and req.conversation_context:
            for item in reversed(req.conversation_context):
                if isinstance(item, dict):
                    if item.get("resolved_location"):
                        last_loc = item["resolved_location"]
                        break
                    wf = item.get("weather_facts")
                    if isinstance(wf, dict) and wf.get("location"):
                        last_loc = wf["location"]
                        break
                    txt = (item.get("text") or item.get("content") or "").lower()
                    for c in KNOWN_CITIES:
                        if c in txt:
                            last_loc = c.title()
                            break
                    if last_loc:
                        break

        # Step 1: NLP Language, Intent, Category, Entity, Date & Session Context Parsing
        parsed_nlp = nlp_parser.parse(
            query=req.query,
            last_location=last_loc,
            last_date=last_dt
        )
        
        intent_cat = parsed_nlp.get("intent_category", "WEATHER_QUERY")
        intent = parsed_nlp["extracted_intent"]
        lang = parsed_nlp["detected_language"]
        loc_name = parsed_nlp["resolved_location"]
        has_explicit_loc = parsed_nlp["has_explicit_location"]
        is_missing_loc = parsed_nlp["missing_location"]
        is_state_query = parsed_nlp.get("is_state_query", False)
        offset = parsed_nlp["date_offset"]
        extracted_state = parsed_nlp.get("extracted_state")

        logger.info(
            f"[NLP DEBUG] RAW QUERY: '{req.query}' | INTENT_CAT: {intent_cat} | INTENT: {intent} | LANG: {lang} | "
            f"EXTRACTED LOC: '{loc_name}' | EXPLICIT LOC: {has_explicit_loc} | STATE: {extracted_state} | "
            f"DATE OFFSET: {offset} ({parsed_nlp.get('date_label')})"
        )

        # Step 2: Hard Weather Gate - Route Non-Weather Queries & Gibberish directly without Geocoding or Weather API
        if intent_cat in ["GREETING", "CONVERSATION", "IDENTITY", "CAPABILITIES", "HELP", "HELP/CAPABILITY", "NON_WEATHER", "UNCLEAR"]:
            logger.info(f"[GATE DEBUG] HARD WEATHER GATE: NON-WEATHER QUERY ({intent_cat}). GEOCODING: NO | WEATHER API: NO")
            grounded_text = grounded_llm_engine.generate_grounded_answer(
                query=req.query,
                parsed_nlp=parsed_nlp,
                weather_facts={},
                risk_eval=None
            )
            resp_type = "clarification" if intent_cat == "UNCLEAR" else "conversation"
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location="",
                resolved_date="",
                response_type=resp_type,
                weather_facts=None,
                risk_evaluation=None,
                grounded_answer=clean_svg_and_markup(grounded_text),
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_non_weather=True,
                is_missing_location=False
            )

        # Step 2b: Multi-Location Comparison Check ("Delhi aur Mumbai ka weather compare karo", "Amritsar aur London Mein tapman Kitna kitna hai compare karo")
        if intent_cat == "COMPARISON" and parsed_nlp.get("comparison_locations") and len(parsed_nlp["comparison_locations"]) >= 2:
            loc1, loc2 = parsed_nlp["comparison_locations"][0], parsed_nlp["comparison_locations"][1]
            geo1 = await geocode_location(loc1)
            geo2 = await geocode_location(loc2)
            if geo1 and geo2:
                # Fetch forecast and current weather for both locations independently
                fc1, fc2 = await asyncio.gather(
                    weather_orchestrator.get_forecast(geo1["latitude"], geo1["longitude"], geo1.get("display_name", loc1), days=3),
                    weather_orchestrator.get_forecast(geo2["latitude"], geo2["longitude"], geo2.get("display_name", loc2), days=3)
                )
                curr1, curr2 = None, None
                try:
                    curr1, curr2 = await asyncio.gather(
                        weather_orchestrator.get_current_weather(geo1["latitude"], geo1["longitude"], geo1.get("display_name", loc1)),
                        weather_orchestrator.get_current_weather(geo2["latitude"], geo2["longitude"], geo2.get("display_name", loc2))
                    )
                except Exception as c_err:
                    logger.warning(f"Error fetching live current weather for comparison: {c_err}")

                day1 = fc1.get("daily", [{}])[0].copy() if fc1.get("daily") else {}
                day2 = fc2.get("daily", [{}])[0].copy() if fc2.get("daily") else {}

                t_curr1 = curr1.get("temperature_c") if curr1 else day1.get("temp_max_c", 25.0)
                t_curr2 = curr2.get("temperature_c") if curr2 else day2.get("temp_max_c", 25.0)

                day1["location"] = geo1.get("display_name", loc1)
                day1["temperature_c"] = t_curr1
                day2["location"] = geo2.get("display_name", loc2)
                day2["temperature_c"] = t_curr2

                comp_text = grounded_llm_engine.generate_comparison_answer(
                    lang=lang,
                    loc1=geo1.get("display_name", loc1),
                    loc2=geo2.get("display_name", loc2),
                    f1=day1,
                    f2=day2,
                    query=req.query
                )
                return WeatherQueryResponse(
                    raw_query=req.query,
                    detected_language=lang,
                    extracted_intent=intent,
                    resolved_location=f"{geo1.get('display_name', loc1)} vs {geo2.get('display_name', loc2)}",
                    resolved_date=day1.get("date", "Today"),
                    response_type="comparison",
                    weather_facts=day1,
                    comparison_data=[day1, day2],
                    risk_evaluation=None,
                    grounded_answer=clean_svg_and_markup(comp_text),
                    source="Open-Meteo Meteorological Service",
                    confidence="HIGH",
                    is_non_weather=False,
                    is_missing_location=False
                )

        # Step 2c: Regional Ranking & Spatial Analysis ("India mein sabse zyada barish kahan hogi?")
        if intent_cat == "RANKING":
            scope = loc_name if loc_name and loc_name.lower() != "location" else "India"
            logger.info(f"[RANKING DEBUG] Executing regional ranking query for scope: '{scope}', date_offset: {offset}")
            ranking_result = await get_regional_ranking(scope=scope, metric="rainfall", date_offset=offset)
            ranking_text = grounded_llm_engine.generate_ranking_answer(lang=lang, ranking_result=ranking_result, query=req.query)
            top_loc = ranking_result.get("top_location") or {}
            top_facts = {
                "location": top_loc.get("city", scope),
                "rain_probability": top_loc.get("rain_probability", 0),
                "precipitation_mm": top_loc.get("precipitation_mm", 0.0),
                "temp_max_c": top_loc.get("temperature_c", 30.0),
                "condition_text": top_loc.get("condition", "Rain"),
                "weather_code": top_loc.get("weather_code", 61)
            } if top_loc else None
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location=scope,
                resolved_date=ranking_result.get("date_label", "Upcoming"),
                response_type="ranking",
                weather_facts=top_facts,
                ranking_data=ranking_result.get("rankings", []),
                risk_evaluation=None,
                grounded_answer=clean_svg_and_markup(ranking_text),
                source="Open-Meteo Regional Analysis",
                confidence="HIGH",
                is_non_weather=False,
                is_missing_location=False
            )

        # Step 3: Handle Unspecified / Missing Location for Weather Query (Ask Clarification Question without Geocoding)
        if is_missing_loc or not loc_name:
            logger.info(f"[GATE DEBUG] HARD WEATHER GATE: MISSING LOCATION FOR WEATHER QUERY. GEOCODING: NO | WEATHER API: NO")
            if intent in ["umbrella", "raincoat"] or "umbrella" in req.query.lower() or "amrela" in req.query.lower() or "ambrella" in req.query.lower():
                if lang == "hi":
                    grounded_text = "क्या आप umbrella लेकर बाहर जाने के लिए मौसम की जानकारी पूछ रहे हैं? कृपया शहर का नाम बताइए।"
                elif lang == "pa":
                    grounded_text = "ਕੀ ਤੁਸੀਂ ਛਤਰੀ ਲੈ ਕੇ ਬਾਹਰ ਜਾਣ ਲਈ ਮੌਸਮ ਬਾਰੇ ਪੁੱਛ ਰਹੇ ਹੋ? ਕਿਰਪਾ ਕਰਕੇ ਸ਼ਹਿਰ ਦਾ ਨਾਮ ਦੱਸੋ।"
                else:
                    grounded_text = "Are you asking whether you should carry an umbrella outdoors? Please specify the city or location you'd like to check."
            else:
                grounded_text = grounded_llm_engine.generate_missing_location_answer(lang)
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location="",
                resolved_date="",
                response_type="clarification",
                weather_facts=None,
                risk_evaluation=None,
                grounded_answer=clean_svg_and_markup(grounded_text),
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_non_weather=False,
                is_missing_location=True
            )

        # Step 4: Geocoding (ONLY FOR VALID WEATHER QUERIES WITH EXPLICIT OR FOLLOWUP LOCATION)
        lat, lon = None, None
        logger.info(f"[GEO DEBUG] GEOCODING CALLED: YES | Query: '{loc_name}' with state_hint: '{extracted_state}'")
        geo = await geocode_location(loc_name, state_hint=extracted_state)
        if geo and geo.get("is_ambiguous"):
            # Ambiguous location match (Section E: Springfield weather -> Ask which Springfield)
            options = geo.get("options", [])
            opt_str = " or ".join(options[:2]) if options else "different states"
            grounded_text = f"Which {geo['name']} do you mean? (for example, {opt_str})"
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location=geo['name'],
                resolved_date="",
                response_type="clarification",
                weather_facts=None,
                risk_evaluation=None,
                grounded_answer=grounded_text,
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_non_weather=False,
                is_missing_location=True
            )

        if geo:
            lat, lon = geo["latitude"], geo["longitude"]
            loc_name = geo.get("display_name") or geo.get("name") or loc_name
            logger.info(f"[GEO DEBUG] Geocoding resolved: '{loc_name}' ({lat}, {lon})")

        # If geocoding failed and no coordinates exist
        if lat is None or lon is None:
            logger.warning(f"[GEO DEBUG] Failed to resolve coordinates for location: '{loc_name}'")
            grounded_text = grounded_llm_engine.generate_missing_location_answer(lang)
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location="",
                resolved_date="",
                response_type="clarification",
                weather_facts=None,
                risk_evaluation=None,
                grounded_answer=grounded_text,
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_non_weather=False,
                is_missing_location=True
            )

        parsed_nlp["resolved_location"] = loc_name

        # Step 4b: Multi-Date Comparison Check ("Friday aur Saturday mein kaunsa din bike ride ke liye better hai?")
        if intent_cat == "COMPARISON" and parsed_nlp.get("comparison_dates") and len(parsed_nlp["comparison_dates"]) >= 2:
            d1_name, d2_name = parsed_nlp["comparison_dates"][0], parsed_nlp["comparison_dates"][1]
            fc = await weather_orchestrator.get_forecast(lat, lon, loc_name, days=8)
            daily_items = fc.get("daily", [])
            f1, f2 = {}, {}
            for item in daily_items:
                if item.get("day_name", "").lower() == d1_name.lower():
                    f1 = item
                if item.get("day_name", "").lower() == d2_name.lower():
                    f2 = item
            if not f1 and len(daily_items) > 1:
                f1 = daily_items[1]
            if not f2 and len(daily_items) > 2:
                f2 = daily_items[2]
            activity_label = "bike ride" if intent in ["cycling", "bike_ride"] or "bike" in req.query.lower() else "outdoor activity"
            comp_date_text = grounded_llm_engine.generate_date_comparison_answer(
                lang=lang, loc=loc_name, d1_name=d1_name, d2_name=d2_name, f1=f1, f2=f2, activity=activity_label
            )
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location=loc_name,
                resolved_date=f"{d1_name} & {d2_name}",
                response_type="weather",
                weather_facts=f1,
                risk_evaluation=None,
                grounded_answer=comp_date_text,
                source="Open-Meteo Meteorological Service",
                confidence="HIGH",
                is_non_weather=False,
                is_missing_location=False
            )

        # Step 5: Fetch Grounded Weather Evidence from Weather Orchestrator for Target Location & Date
        logger.info(f"[WEATHER API DEBUG] WEATHER API CALLED: YES | Location: '{loc_name}' ({lat}, {lon})")
        forecast = await weather_orchestrator.get_forecast(lat, lon, loc_name, days=max(offset + 2, 7) if offset >= 0 else 7)
        warnings = await weather_orchestrator.get_warnings(lat, lon, loc_name)

        # If current temperature or real-time abhi/vartman requested, fetch live current weather feed
        current_data = None
        if parsed_nlp.get("is_current") or intent_cat == "WEATHER_CURRENT" or offset == 0:
            try:
                current_data = await weather_orchestrator.get_current_weather(lat, lon, loc_name)
            except Exception as ce:
                logger.warning(f"Failed to fetch live current weather: {ce}")

        daily_list = forecast.get("daily", [])
        day_idx = max(0, min(offset, len(daily_list) - 1)) if offset >= 0 else 0
        target_day = daily_list[day_idx] if daily_list else {}

        is_curr_query = bool(
            parsed_nlp.get("is_current") or 
            (offset == 0 and any(k in req.query.lower() for k in ["now", "abhi", "is rain", "right now", "happen", "chal raha"]))
        )

        real_curr_temp = current_data.get("temperature_c") if (current_data and offset == 0) else target_day.get("temp_max_c", 30.0)
        real_wind = current_data.get("wind_speed_kmh") if (current_data and offset == 0) else target_day.get("max_wind_kmh", 12.0)
        real_humidity = current_data.get("humidity", 60.0) if (current_data and offset == 0) else 60.0
        curr_condition = current_data.get("condition_text") or target_day.get("condition_text", "Partly Cloudy") if current_data else target_day.get("condition_text", "Partly Cloudy")
        curr_weather_code = current_data.get("weather_code") if (current_data and current_data.get("weather_code") is not None) else target_day.get("weather_code", 0)
        curr_precip = current_data.get("precipitation_mm", 0.0) if current_data else target_day.get("precipitation_mm", 0.0)
        curr_rain_prob = current_data.get("rain_probability", (80.0 if curr_precip > 0.1 else 10.0)) if current_data else target_day.get("rain_probability", 20.0)

        weather_facts = {
            "location": loc_name,
            "latitude": lat,
            "longitude": lon,
            "date": "Today (Current Observation)" if is_curr_query else target_day.get("date", parsed_nlp.get("date_label", "Today")),
            "is_current_observation": is_curr_query,
            "rain_probability": curr_rain_prob if is_curr_query else target_day.get("rain_probability", 20.0),
            "precipitation_mm": curr_precip if is_curr_query else target_day.get("precipitation_mm", 0.0),
            "temp_max_c": target_day.get("temp_max_c", 30.0),
            "temp_min_c": target_day.get("temp_min_c", 22.0),
            "temperature_c": real_curr_temp,
            "feels_like_c": current_data.get("feels_like_c", real_curr_temp) if current_data else real_curr_temp,
            "max_wind_kmh": real_wind,
            "wind_speed_kmh": real_wind,
            "humidity": real_humidity,
            "condition_text": curr_condition if is_curr_query else target_day.get("condition_text", "Partly Cloudy"),
            "weather_code": curr_weather_code if is_curr_query else target_day.get("weather_code", 0),
            "uv_index": target_day.get("uv_index_max", 5.0),
            "source": forecast.get("source", "Open-Meteo Meteorological Service"),
            "updated_at": forecast.get("updated_at", "Just now"),
            "confidence": forecast.get("confidence", "HIGH"),
            "disagreement_note": forecast.get("disagreement_note"),
            "hourly": forecast.get("hourly", []),
            "daily": forecast.get("daily", [])
        }

        # Step 6: Run Deterministic Risk Engine
        context_type = req.context_type if req.context_type != "general" else intent
        risk_eval = risk_engine.evaluate(
            weather_data=weather_facts,
            warnings=warnings,
            context=context_type
        )

        # Step 7: Grounded Response Generation
        grounded_text = grounded_llm_engine.generate_grounded_answer(
            query=req.query,
            parsed_nlp=parsed_nlp,
            weather_facts=weather_facts,
            risk_eval=risk_eval
        )
        grounded_text = clean_svg_and_markup(grounded_text)

        # Step 8: Log Query to DB asynchronously
        try:
            db_query = WeatherQuery(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location=loc_name,
                resolved_date=target_day.get("date", ""),
                risk_level=risk_eval.risk_level if risk_eval else "LOW",
                grounded_response=grounded_text,
                confidence=forecast.get("confidence", "HIGH")
            )
            db.add(db_query)
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to log query to DB: {e}")

        resp_type = "activity" if intent_cat in ["ACTIVITY_SUITABILITY", "AGRICULTURE", "OUTDOOR_EVENT", "BIKE_RIDE", "CYCLING"] else "weather"

        return WeatherQueryResponse(
            raw_query=req.query,
            detected_language=lang,
            extracted_intent=intent,
            resolved_location=loc_name,
            resolved_date=target_day.get("date", parsed_nlp.get("date_label", "Today")),
            response_type=resp_type,
            weather_facts=weather_facts,
            risk_evaluation=risk_eval,
            grounded_answer=grounded_text,
            source=forecast.get("source", "Open-Meteo"),
            updated_at=forecast.get("updated_at", "Just now"),
            confidence=forecast.get("confidence", "HIGH"),
            disagreement_details=forecast.get("disagreement_note"),
            is_non_weather=False,
            is_missing_location=False,
            is_state_query=is_state_query
        )

    except Exception as e:
        logger.error(f"Error in process_weather_query: {e}")
        raise HTTPException(status_code=500, detail=f"Weather intelligence query processing failed: {str(e)}")


@router.post("/advisory", response_model=WeatherQueryResponse)
async def get_advisory(
    req: WeatherQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    return await process_weather_query(req, db)
