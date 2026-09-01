import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.cache.redis_client import cache_manager
from app.api.health import router as health_router
from app.api.weather import router as weather_router
from app.api.chat import router as chat_router
from app.api.voice import router as voice_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("weathergpt")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing WeatherGPT Backend Services...")
    # Initialize DB tables
    await init_db()
    # Connect Redis
    await cache_manager.connect()
    logger.info("WeatherGPT Backend Ready.")
    yield
    logger.info("Shutting down WeatherGPT Backend Services...")


app = FastAPI(
    title="WeatherGPT — Conversational Weather Intelligence & Decision Support",
    description="Smart India Hackathon 2026 (SIH26068) Weather Intelligence Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(voice_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to WeatherGPT API — Conversational Weather Intelligence & Decision Support Platform",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }
