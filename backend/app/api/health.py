import datetime
from fastapi import APIRouter
from app.config import settings
from app.cache.redis_client import cache_manager

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "WeatherGPT Intelligence Platform API",
        "version": "1.0.0-SIH26068",
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "demo_mode": settings.DEMO_MODE,
        "redis_connected": cache_manager.use_redis,
        "llm_provider": "Gemini Grounded Engine" if settings.GEMINI_API_KEY else "Grounded Fallback Engine"
    }
