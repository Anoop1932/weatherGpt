from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.weather_schemas import VoiceQueryRequest, WeatherQueryResponse, WeatherQueryRequest
from app.api.chat import process_weather_query

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])


@router.post("/query", response_model=WeatherQueryResponse)
async def process_voice_query(
    req: VoiceQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    query_req = WeatherQueryRequest(
        query=req.audio_text,
        location=req.location,
        language=req.language,
        last_location=req.last_location,
        last_date=req.last_date,
        last_intent=req.last_intent
    )
    return await process_weather_query(query_req, db)
