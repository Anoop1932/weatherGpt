import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.ai.nlp_parser import nlp_parser
from app.ai.grounded_llm import grounded_llm_engine
from app.weather.orchestrator import weather_orchestrator
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
        # Step 1: NLP Language, Intent, Entity, Date & Session Context Parsing
        parsed_nlp = nlp_parser.parse(
            query=req.query,
            last_location=req.last_location,
            last_date=req.last_date
        )
        
        intent = parsed_nlp["extracted_intent"]
        lang = parsed_nlp["detected_language"]
        loc_name = parsed_nlp["resolved_location"]
        has_explicit_loc = parsed_nlp["has_explicit_location"]
        is_missing_loc = parsed_nlp["missing_location"]
        is_state_query = parsed_nlp.get("is_state_query", False)
        offset = parsed_nlp["date_offset"]
        extracted_state = parsed_nlp.get("extracted_state")

        logger.info(
            f"[NLP DEBUG] RAW QUERY: '{req.query}' | INTENT: {intent} | LANG: {lang} | "
            f"EXTRACTED LOC: '{loc_name}' | EXPLICIT LOC: {has_explicit_loc} | STATE: {extracted_state} | "
            f"DATE OFFSET: {offset} ({parsed_nlp.get('date_label')})"
        )

        # Step 2: Route Non-Weather Queries directly (Greetings, Meta, Thanks)
        if intent in ["non_weather_greeting", "non_weather_meta", "non_weather_thanks"]:
            grounded_text = grounded_llm_engine.generate_grounded_answer(
                query=req.query,
                parsed_nlp=parsed_nlp,
                weather_facts={},
                risk_eval=None
            )
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location="",
                resolved_date="",
                grounded_answer=grounded_text,
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_non_weather=True
            )

        # Step 3: Handle Unspecified / Missing Location (Ask Clarification Question)
        if is_missing_loc and not req.location:
            grounded_text = grounded_llm_engine.generate_missing_location_answer(lang)
            return WeatherQueryResponse(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location="",
                resolved_date="",
                grounded_answer=grounded_text,
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_missing_location=True
            )

        # If location was not in query string but UI location is available as fallback
        if not loc_name and req.location:
            loc_name = req.location

        # Step 4: Robust Geocoding with State & Country Context
        lat, lon = None, None
        if loc_name:
            logger.info(f"[GEO DEBUG] Geocoding query: '{loc_name}' with state_hint: '{extracted_state}'")
            geo = await geocode_location(loc_name, state_hint=extracted_state)
            if geo:
                lat, lon = geo["latitude"], geo["longitude"]
                loc_name = geo.get("display_name") or geo.get("name") or loc_name
                logger.info(f"[GEO DEBUG] Geocoding resolved: '{loc_name}' ({lat}, {lon})")
            elif req.latitude is not None and req.longitude is not None:
                lat, lon = req.latitude, req.longitude
        elif req.latitude is not None and req.longitude is not None:
            lat, lon = req.latitude, req.longitude
            loc_name = req.location or "Current Location"

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
                grounded_answer=grounded_text,
                source="WeatherGPT Assistant",
                confidence="HIGH",
                is_missing_location=True
            )

        parsed_nlp["resolved_location"] = loc_name

        # Step 5: Fetch Grounded Weather Evidence from Weather Orchestrator for Target Location & Date
        forecast = await weather_orchestrator.get_forecast(lat, lon, loc_name, days=max(offset + 2, 7))
        warnings = await weather_orchestrator.get_warnings(lat, lon, loc_name)

        daily_list = forecast.get("daily", [])
        target_day = daily_list[min(offset, len(daily_list) - 1)] if daily_list else {}

        weather_facts = {
            "location": loc_name,
            "latitude": lat,
            "longitude": lon,
            "date": target_day.get("date", parsed_nlp.get("date_label", "Today")),
            "rain_probability": target_day.get("rain_probability", 20.0),
            "precipitation_mm": target_day.get("precipitation_mm", 0.0),
            "temp_max_c": target_day.get("temp_max_c", 30.0),
            "temp_min_c": target_day.get("temp_min_c", 22.0),
            "temperature_c": target_day.get("temp_max_c", 30.0),
            "max_wind_kmh": target_day.get("max_wind_kmh", 12.0),
            "condition_text": target_day.get("condition_text", "Partly Cloudy"),
            "weather_code": target_day.get("weather_code", 0),
            "uv_index": target_day.get("uv_index_max", 5.0),
            "source": forecast.get("source", "Open-Meteo Meteorological Service"),
            "updated_at": forecast.get("updated_at", "Just now"),
            "confidence": forecast.get("confidence", "HIGH"),
            "disagreement_note": forecast.get("disagreement_note")
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

        return WeatherQueryResponse(
            raw_query=req.query,
            detected_language=lang,
            extracted_intent=intent,
            resolved_location=loc_name,
            resolved_date=target_day.get("date", parsed_nlp.get("date_label", "Today")),
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
