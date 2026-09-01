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
            prob = 65.0 if i == 1 else (40.0 if i == 2 else 20.0)
            daily.append({
                "date": day_dt.strftime("%Y-%m-%d"),
                "day_name": day_dt.strftime("%a"),
                "temp_max_c": 32.0 + (i % 2),
                "temp_min_c": 22.0,
                "rain_probability": prob,
                "precipitation_mm": 12.5 if prob > 50 else 0.0,
                "max_wind_kmh": 15.0,
                "condition_text": "Moderate Rain" if prob > 50 else "Partly Cloudy",
                "weather_code": 63 if prob > 50 else 2,
                "uv_index_max": 6.0,
                "risk_level": "HIGH" if prob > 60 else "LOW"
            })

        for h in range(24):
            hourly.append({
                "time": f"{h:02d}:00",
                "temperature_c": round(24.0 + (h % 10), 1),
                "rain_probability": 65.0 if 12 <= h <= 18 else 20.0,
                "precipitation_mm": 2.5 if 12 <= h <= 18 else 0.0,
                "humidity": 70.0,
                "wind_speed_kmh": 12.0,
                "condition_text": "Rain Showers" if 12 <= h <= 18 else "Partly Cloudy",
                "weather_code": 80 if 12 <= h <= 18 else 2
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
        return [{
            "id": "demo-warn-001",
            "location": location_name,
            "warning_type": "Advisory Rain Watch",
            "severity": "MODERATE",
            "headline": f"Rain & Wind Advisory for {location_name}",
            "description": f"Rain probability is approximately 65% tomorrow afternoon. Outdoor activities and pesticide spraying should be rescheduled.",
            "affected_area": f"{location_name} Region",
            "issued_at": datetime.datetime.now().strftime("%Y-%m-%d 09:00 IST"),
            "valid_until": (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime("%Y-%m-%d 09:00 IST"),
            "source": "WeatherGPT Verified Demo Dataset"
        }]
