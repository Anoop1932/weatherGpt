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
    language: Optional[str] = "auto" # auto, en, hi, pa
    context_type: Optional[str] = "general" # general, travel, agriculture, event
    last_location: Optional[str] = None
    last_locations: Optional[List[str]] = None
    last_date: Optional[str] = None
    last_time_range: Optional[str] = None
    last_intent: Optional[str] = None
    last_activity: Optional[str] = None
    last_metric: Optional[str] = None
    last_origin: Optional[str] = None
    last_destination: Optional[str] = None
    last_response_type: Optional[str] = None
    conversation_context: Optional[List[Dict[str, Any]]] = None


class WeatherFactSet(BaseModel):
    location: str
    latitude: float
    longitude: float
    timezone: str = "auto"
    requested_date: str
    is_current_observation: bool = False
    temperature_c: float
    temp_max_c: float
    temp_min_c: float
    feels_like_c: float
    rain_probability: float
    daily_rain_probability_max: float
    current_rain_probability: float
    precipitation_mm: float
    wind_speed_kmh: float
    max_wind_kmh: float
    humidity: float
    condition_text: str
    weather_code: int
    uv_index: float
    hourly: Optional[List[Dict[str, Any]]] = None
    daily: Optional[List[Dict[str, Any]]] = None
    source: str = "Open-Meteo Meteorological Service"
    updated_at: str = "Just now"
    confidence: str = "HIGH"
    disagreement_note: Optional[str] = None


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
    response_type: str = Field("weather", description="weather | conversation | clarification | error | comparison | ranking | activity | travel | regional_analysis")
    weather_facts: Optional[Dict[str, Any]] = None
    comparison_data: Optional[List[Dict[str, Any]]] = None
    ranking_data: Optional[List[Dict[str, Any]]] = None
    travel_data: Optional[Dict[str, Any]] = None
    risk_evaluation: Optional[RiskEvaluation] = None
    grounded_answer: str
    source: str = "WeatherGPT Intelligence Engine"
    updated_at: str = "Just now"
    confidence: str = "HIGH"
    disagreement_details: Optional[str] = None
    is_non_weather: bool = False
    is_missing_location: bool = False
    is_state_query: bool = False


class VoiceQueryRequest(BaseModel):
    audio_text: str
    language: str = "en"
    location: Optional[str] = None
    last_location: Optional[str] = None
    last_date: Optional[str] = None
    last_intent: Optional[str] = None


class HistoricalWeatherItem(BaseModel):
    date: str
    max_temp_c: float
    min_temp_c: float
    precipitation_mm: float
    max_wind_kmh: float
    condition: str
