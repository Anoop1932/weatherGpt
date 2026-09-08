import datetime
from typing import Dict, Any, List
from app.weather.base import WeatherProvider


class FallbackProvider(WeatherProvider):

    @property
    def provider_name(self) -> str:
        return "WeatherGPT Demo Fallback Engine"

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        return {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": 31.0,
            "feels_like_c": 34.0,
            "humidity": 65.0,
            "wind_speed_kmh": 14.0,
            "wind_direction_deg": 180.0,
            "pressure_hpa": 1010.0,
            "visibility_km": 8.0,
            "rain_probability": 65.0,
            "uv_index": 5.8,
            "condition_text": "Moderate Rain Likely",
            "weather_code": 63,
            "source": self.provider_name,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST")
        }

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        today = datetime.date.today()
        daily = []
        hourly = []

        for i in range(days):
            day_dt = today + datetime.timedelta(days=i)
            # Factual baseline: mild default variation without hardcoded 65% rain spikes
            prob = 15.0 + (i * 2 % 15)
            daily.append({
                "date": day_dt.strftime("%Y-%m-%d"),
                "day_name": day_dt.strftime("%a"),
                "temp_max_c": 31.0 + (i % 3),
                "temp_min_c": 22.0,
                "rain_probability": prob,
                "precipitation_mm": 0.0,
                "max_wind_kmh": 12.0,
                "condition_text": "Partly Cloudy",
                "weather_code": 2,
                "uv_index_max": 5.0,
                "risk_level": "LOW"
            })

        for h in range(24):
            hourly.append({
                "time": f"{h:02d}:00",
                "temperature_c": round(24.0 + (h % 8), 1),
                "rain_probability": 15.0,
                "precipitation_mm": 0.0,
                "humidity": 55.0,
                "wind_speed_kmh": 10.0,
                "condition_text": "Partly Cloudy",
                "weather_code": 2
            })

        return {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "source": self.provider_name,
            "confidence": "MODERATE",
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M IST"),
            "daily": daily,
            "hourly": hourly
        }

    async def get_warnings(self, lat: float, lon: float, location_name: str) -> List[Dict[str, Any]]:
        # Never invent or fabricate fake warning alerts when official warnings are unavailable
        return []
