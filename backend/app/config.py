import os
from typing import List, Union
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./weathergpt.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    DEMO_MODE: bool = False
    DEFAULT_LOCATION: str = "Amritsar"
    DEFAULT_LAT: float = 31.6340
    DEFAULT_LON: float = 74.8723
    
    SECRET_KEY: str = "weathergpt_sih2026_super_secret_key"
    
    # Provider timeouts (seconds)
    WEATHER_API_TIMEOUT: float = 8.0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
