import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    language_preference = Column(String(10), default="en")
    default_location = Column(String(100), default="Amritsar")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    temperature_c = Column(Float)
    feels_like_c = Column(Float)
    humidity = Column(Float)
    wind_speed_kmh = Column(Float)
    wind_direction_deg = Column(Float)
    pressure_hpa = Column(Float)
    visibility_km = Column(Float)
    condition_text = Column(String(100))
    weather_code = Column(Integer)
    source = Column(String(50), index=True)
    observed_at = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    forecast_date = Column(String(20), index=True) # YYYY-MM-DD
    data_json = Column(JSON) # hourly & daily metrics
    source = Column(String(50), index=True)
    confidence = Column(String(20), default="HIGH") # HIGH, MODERATE, LOW
    issued_at = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)


class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), index=True)
    warning_type = Column(String(100)) # Heavy Rain, Thunderstorm, Heatwave, Fog
    severity = Column(String(20), index=True) # LOW, MODERATE, HIGH, SEVERE
    description = Column(Text)
    affected_area = Column(String(200))
    source = Column(String(100), default="IMD / Official Meteorological Center")
    issued_at = Column(DateTime)
    valid_until = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)


class WeatherQuery(Base):
    __tablename__ = "weather_queries"

    id = Column(Integer, primary_key=True, index=True)
    raw_query = Column(Text, nullable=False)
    detected_language = Column(String(10)) # en, hi
    extracted_intent = Column(String(50)) # forecast, travel, agriculture, event, warning
    resolved_location = Column(String(100))
    resolved_date = Column(String(20))
    risk_level = Column(String(20))
    grounded_response = Column(Text)
    confidence = Column(String(20))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("weather_queries.id"), nullable=True)
    category = Column(String(50)) # travel, agriculture, outdoor, safety
    risk_level = Column(String(20))
    advice_text = Column(Text)
    evidence_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class HistoricalWeather(Base):
    __tablename__ = "historical_weather"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(100), index=True)
    date = Column(String(20), index=True)
    max_temp_c = Column(Float)
    min_temp_c = Column(Float)
    precipitation_mm = Column(Float)
    max_wind_kmh = Column(Float)
    source = Column(String(50))
