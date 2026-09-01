from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class LocationInfo(BaseModel):
    name: str
    state: Optional[str] = None
    country: str = "India"
    latitude: float
    longitude: float


class CurrentWeatherResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature_c: float
    feels_like_c: float
    humidity: float
    wind_speed_kmh: float
    wind_direction_deg: float
    pressure_hpa: float
    visibility_km: float
    rain_probability: float
    uv_index: float
    condition_text: str
    weather_code: int
    source: str
    confidence: str = "HIGH"
    updated_at: str
    is_cached: bool = False


class HourlyForecastItem(BaseModel):
    time: str # e.g. "14:00" or ISO
    temperature_c: float
    rain_probability: float
    precipitation_mm: float
    humidity: float
    wind_speed_kmh: float
    condition_text: str
    weather_code: int


class DailyForecastItem(BaseModel):
    date: str # YYYY-MM-DD
    day_name: str # Mon, Tue, etc.
    temp_max_c: float
    temp_min_c: float
    rain_probability: float
    precipitation_mm: float
    max_wind_kmh: float
    condition_text: str
    weather_code: int
    uv_index_max: float
    risk_level: str = "LOW"


class ForecastResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    source: str
    confidence: str = "HIGH"
    updated_at: str
    disagreement_note: Optional[str] = None
    hourly: List[HourlyForecastItem]
    daily: List[DailyForecastItem]


class WarningItem(BaseModel):
    id: str
    location: str
    warning_type: str
    severity: str # LOW, MODERATE, HIGH, SEVERE
    headline: str
    description: str
    affected_area: str
    issued_at: str
    valid_until: str
    source: str


class WeatherQueryRequest(BaseModel):
    query: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    language: Optional[str] = "auto" # auto, en, hi
    context_type: Optional[str] = "general" # general, travel, agriculture, event


class RiskEvaluation(BaseModel):
    risk_level: str # LOW, MODERATE, HIGH, SEVERE
    category: str # travel, agriculture, event, general
    reasons: List[str]
    recommendation: str
    evidence: Dict[str, Any]
    confidence: str


class WeatherQueryResponse(BaseModel):
    raw_query: str
    detected_language: str
    extracted_intent: str
    resolved_location: str
    resolved_date: str
    weather_facts: Dict[str, Any]
    risk_evaluation: RiskEvaluation
    grounded_answer: str
    source: str
    updated_at: str
    confidence: str
    disagreement_details: Optional[str] = None


class VoiceQueryRequest(BaseModel):
    audio_text: str
    language: str = "en"
    location: Optional[str] = None


class HistoricalWeatherItem(BaseModel):
    date: str
    max_temp_c: float
    min_temp_c: float
    precipitation_mm: float
    max_wind_kmh: float
    condition: str
