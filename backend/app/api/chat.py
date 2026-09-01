import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.ai.nlp_parser import nlp_parser
from app.ai.grounded_llm import grounded_llm_engine
from app.weather.orchestrator import weather_orchestrator
from app.risk.engine import risk_engine
from app.utils.geocoding import geocode_location
from app.schemas.weather_schemas import WeatherQueryRequest, WeatherQueryResponse
from app.models.db_models import WeatherQuery

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["AI Conversational Intelligence"])


@router.post("/query", response_model=WeatherQueryResponse)
async def process_weather_query(
    req: WeatherQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Step 1: NLP Language, Intent, Entity & Date Parsing
        parsed_nlp = nlp_parser.parse(req.query, default_location=req.location or "Amritsar")
        loc_name = parsed_nlp["resolved_location"]
        has_explicit_loc = parsed_nlp.get("has_explicit_location", False)
        offset = parsed_nlp["date_offset"]
        intent = parsed_nlp["extracted_intent"]
        
        # Message detected language takes precedence for native prompt responses
        lang = parsed_nlp["detected_language"]

        # Step 2: Location Geocoding with Explicit Priority
        if has_explicit_loc:
            try:
                geo = await geocode_location(loc_name)
                lat, lon = geo["latitude"], geo["longitude"]
                loc_name = geo.get("display_name") or geo.get("name") or loc_name
            except Exception as e:
                logger.warning(f"Geocoding fallback for {loc_name}: {e}")
                lat, lon = req.latitude or 31.634, req.longitude or 74.8723
        else:
            # Fallback to UI active location when no location is explicitly mentioned in query
            loc_name = req.location or "Amritsar"
            if req.latitude is not None and req.longitude is not None:
                lat, lon = req.latitude, req.longitude
            else:
                try:
                    geo = await geocode_location(loc_name)
                    lat, lon = geo["latitude"], geo["longitude"]
                    loc_name = geo.get("display_name") or geo.get("name") or loc_name
                except Exception as e:
                    lat, lon = 31.6340, 74.8723

        # Update parsed_nlp resolved_location for grounded engine
        parsed_nlp["resolved_location"] = loc_name

        # Step 3: Fetch Grounded Weather Evidence from Weather Orchestrator for Target Location & Date
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
            "max_wind_kmh": target_day.get("max_wind_kmh", 12.0),
            "condition_text": target_day.get("condition_text", "Partly Cloudy"),
            "source": forecast.get("source", "Open-Meteo Meteorological Service"),
            "updated_at": forecast.get("updated_at", "Just now"),
            "confidence": forecast.get("confidence", "HIGH"),
            "disagreement_note": forecast.get("disagreement_note")
        }

        # Step 4: Run Deterministic Risk Engine
        context_type = req.context_type if req.context_type != "general" else intent
        risk_eval = risk_engine.evaluate(
            weather_data=weather_facts,
            warnings=warnings,
            context=context_type
        )

        # Step 5: Grounded Response Generation in User's Message Language
        grounded_text = grounded_llm_engine.generate_grounded_answer(
            query=req.query,
            parsed_nlp=parsed_nlp,
            weather_facts=weather_facts,
            risk_eval=risk_eval
        )

        # Step 6: Log Query to DB asynchronously
        try:
            db_query = WeatherQuery(
                raw_query=req.query,
                detected_language=lang,
                extracted_intent=intent,
                resolved_location=loc_name,
                resolved_date=target_day.get("date", ""),
                risk_level=risk_eval.risk_level,
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
            disagreement_details=forecast.get("disagreement_note")
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
