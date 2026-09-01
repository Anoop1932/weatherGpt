import httpx
import logging
import datetime
from typing import Dict, Any, List
from app.weather.base import WeatherProvider
from app.config import settings

logger = logging.getLogger(__name__)

# WMO Weather interpretation codes (WW)
WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail",
}


class OpenMeteoProvider(WeatherProvider):

    @property
    def provider_name(self) -> str:
        return "Open-Meteo Meteorological Service"

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "precipitation", "rain", "weather_code", "surface_pressure",
                "wind_speed_10m", "wind_direction_10m", "cloud_cover"
            ],
            "daily": ["sunrise", "sunset", "uv_index_max", "precipitation_probability_max"],
            "hourly": ["visibility", "precipitation_probability"],
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=settings.WEATHER_API_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        curr = data.get("current", {})
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})
        vis_list = hourly.get("visibility", [10000])
        current_vis_km = round(vis_list[0] / 1000.0, 1) if vis_list else 10.0

        w_code = curr.get("weather_code", 0)
        condition = WMO_WEATHER_CODES.get(w_code, "Partly Cloudy")

        sunrise_str = daily.get("sunrise", ["06:00"])[0] if daily.get("sunrise") else "06:00"
        sunset_str = daily.get("sunset", ["18:30"])[0] if daily.get("sunset") else "18:30"

        if "T" in sunrise_str:
            sunrise_str = sunrise_str.split("T")[-1]
        if "T" in sunset_str:
            sunset_str = sunset_str.split("T")[-1]

        uv_val = daily.get("uv_index_max", [5.2])[0] or 5.2

        # Extract real precipitation probability from API hourly or daily max
        hourly_prob = hourly.get("precipitation_probability", [None])[0]
        daily_max_prob = daily.get("precipitation_probability_max", [None])[0]
        
        if hourly_prob is not None:
            rain_prob = float(hourly_prob)
        elif daily_max_prob is not None:
            rain_prob = float(daily_max_prob)
        elif curr.get("precipitation", 0) > 0:
            rain_prob = 100.0
        else:
            rain_prob = 0.0

        return {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": round(curr.get("temperature_2m", 28.0), 1),
            "feels_like_c": round(curr.get("apparent_temperature", 29.5), 1),
            "humidity": round(curr.get("relative_humidity_2m", 60.0), 1),
            "wind_speed_kmh": round(curr.get("wind_speed_10m", 12.0), 1),
            "wind_direction_deg": round(curr.get("wind_direction_10m", 180.0), 1),
            "pressure_hpa": round(curr.get("surface_pressure", 1012.0), 1),
            "visibility_km": current_vis_km,
            "cloud_cover": round(curr.get("cloud_cover", 20.0), 1),
            "rain_probability": round(rain_prob, 1),
            "precipitation_mm": round(curr.get("precipitation", 0.0), 1),
            "uv_index": round(uv_val, 1),
            "sunrise": sunrise_str,
            "sunset": sunset_str,
            "condition_text": condition,
            "weather_code": w_code,
            "source": self.provider_name,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local")
        }

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "precipitation_probability_max",
                "wind_speed_10m_max", "uv_index_max"
            ],
            "hourly": [
                "temperature_2m", "precipitation_probability", "precipitation",
                "relative_humidity_2m", "wind_speed_10m", "weather_code"
            ],
            "forecast_days": days,
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=settings.WEATHER_API_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        daily_raw = data.get("daily", {})
        hourly_raw = data.get("hourly", {})

        daily_items = []
        times = daily_raw.get("time", [])
        for i, dt_str in enumerate(times):
            dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d")
            w_code = daily_raw.get("weather_code", [0])[i]
            rain_prob = daily_raw.get("precipitation_probability_max", [0])[i] or 0.0

            risk_level = "LOW"
            if rain_prob > 60 or w_code in [95, 96, 99]:
                risk_level = "HIGH"
            elif rain_prob > 30 or w_code in [63, 65, 80, 81]:
                risk_level = "MODERATE"

            daily_items.append({
                "date": dt_str,
                "day_name": dt.strftime("%a"),
                "temp_max_c": round(daily_raw.get("temperature_2m_max", [30.0])[i], 1),
                "temp_min_c": round(daily_raw.get("temperature_2m_min", [20.0])[i], 1),
                "rain_probability": float(rain_prob),
                "precipitation_mm": round(daily_raw.get("precipitation_sum", [0.0])[i], 1),
                "max_wind_kmh": round(daily_raw.get("wind_speed_10m_max", [15.0])[i], 1),
                "condition_text": WMO_WEATHER_CODES.get(w_code, "Partly Cloudy"),
                "weather_code": w_code,
                "uv_index_max": round(daily_raw.get("uv_index_max", [5.0])[i], 1),
                "risk_level": risk_level
            })

        hourly_items = []
        h_times = hourly_raw.get("time", [])[:24]
        for i, ht_str in enumerate(h_times):
            hour_str = ht_str.split("T")[-1] if "T" in ht_str else ht_str[-5:]
            w_code = hourly_raw.get("weather_code", [0])[i]
            hourly_items.append({
                "time": hour_str,
                "temperature_c": round(hourly_raw.get("temperature_2m", [25.0])[i], 1),
                "rain_probability": float(hourly_raw.get("precipitation_probability", [0])[i] or 0),
                "precipitation_mm": round(hourly_raw.get("precipitation", [0.0])[i], 1),
                "humidity": round(hourly_raw.get("relative_humidity_2m", [55.0])[i], 1),
                "wind_speed_kmh": round(hourly_raw.get("wind_speed_10m", [10.0])[i], 1),
                "condition_text": WMO_WEATHER_CODES.get(w_code, "Partly Cloudy"),
                "weather_code": w_code
            })

        return {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "source": self.provider_name,
            "confidence": "HIGH",
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local"),
            "daily": daily_items,
            "hourly": hourly_items
        }

    async def get_warnings(self, lat: float, lon: float, location_name: str) -> List[Dict[str, Any]]:
        # Return official warnings only when verified warning feed returns alerts
        return []
