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

    async def fetch_complete_weather(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        """
        Fetches unified meteorological data in ONE single HTTP call to Open-Meteo,
        returning synchronized current observation, daily forecasts, and hourly items.
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m", "relative_humidity_2m", "apparent_temperature",
                "precipitation", "rain", "weather_code", "surface_pressure",
                "wind_speed_10m", "wind_direction_10m", "cloud_cover"
            ],
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "precipitation_sum", "precipitation_probability_max",
                "wind_speed_10m_max", "uv_index_max", "sunrise", "sunset"
            ],
            "hourly": [
                "temperature_2m", "precipitation_probability", "precipitation",
                "relative_humidity_2m", "wind_speed_10m", "weather_code", "visibility"
            ],
            "forecast_days": min(max(days, 14), 16),
            "timezone": "auto"
        }

        async with httpx.AsyncClient(timeout=settings.WEATHER_API_TIMEOUT) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        curr = data.get("current", {})
        daily_raw = data.get("daily", {})
        hourly_raw = data.get("hourly", {})

        # Parse sunrise / sunset
        sunrises = daily_raw.get("sunrise", ["06:00"])
        sunsets = daily_raw.get("sunset", ["18:30"])
        sunrise_str = sunrises[0].split("T")[-1] if (sunrises and "T" in sunrises[0]) else (sunrises[0] if sunrises else "06:00")
        sunset_str = sunsets[0].split("T")[-1] if (sunsets and "T" in sunsets[0]) else (sunsets[0] if sunsets else "18:30")

        # Parse Current Observation Condition
        w_code_curr = curr.get("weather_code", 0)
        cond_curr = WMO_WEATHER_CODES.get(w_code_curr, "Partly Cloudy")

        # Find current hour precipitation probability from hourly timeline
        curr_time_str = curr.get("time", "")
        h_times = hourly_raw.get("time", [])
        curr_hour_idx = 0
        if curr_time_str and h_times:
            curr_prefix = curr_time_str[:13]
            for idx, ht in enumerate(h_times):
                if ht.startswith(curr_prefix):
                    curr_hour_idx = idx
                    break

        h_probs = hourly_raw.get("precipitation_probability", [])
        hour_prob = float(h_probs[curr_hour_idx] if curr_hour_idx < len(h_probs) and h_probs[curr_hour_idx] is not None else 0.0)

        # If currently precipitation is detected, current rain prob is 100%
        curr_precip = round(float(curr.get("precipitation", 0.0)), 1)
        curr_rain_prob = 100.0 if (curr_precip > 0.0 or curr.get("rain", 0.0) > 0.0) else hour_prob

        # Daily maximum rain probability for today
        daily_max_prob = float(daily_raw.get("precipitation_probability_max", [0.0])[0] or 0.0)

        vis_list = hourly_raw.get("visibility", [10000])
        curr_vis_km = round(vis_list[curr_hour_idx] / 1000.0, 1) if curr_hour_idx < len(vis_list) else 10.0

        uv_val = round(float(daily_raw.get("uv_index_max", [5.0])[0] or 5.0), 1)

        # Build Daily Items
        daily_items = []
        times = daily_raw.get("time", [])
        for i, dt_str in enumerate(times):
            dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d")
            w_code = daily_raw.get("weather_code", [0])[i]
            rain_prob_day = float(daily_raw.get("precipitation_probability_max", [0])[i] or 0.0)

            risk_level = "LOW"
            if rain_prob_day > 60 or w_code in [95, 96, 99]:
                risk_level = "HIGH"
            elif rain_prob_day > 30 or w_code in [63, 65, 80, 81]:
                risk_level = "MODERATE"

            daily_items.append({
                "date": dt_str,
                "day_name": dt.strftime("%a"),
                "temp_max_c": round(float(daily_raw.get("temperature_2m_max", [30.0])[i]), 1),
                "temp_min_c": round(float(daily_raw.get("temperature_2m_min", [20.0])[i]), 1),
                "rain_probability": rain_prob_day,
                "precipitation_mm": round(float(daily_raw.get("precipitation_sum", [0.0])[i]), 1),
                "max_wind_kmh": round(float(daily_raw.get("wind_speed_10m_max", [15.0])[i]), 1),
                "condition_text": WMO_WEATHER_CODES.get(w_code, "Partly Cloudy"),
                "weather_code": w_code,
                "uv_index_max": round(float(daily_raw.get("uv_index_max", [5.0])[i] or 5.0), 1),
                "risk_level": risk_level
            })

        # Build Hourly Items (First 24 hours)
        hourly_items = []
        for i, ht_str in enumerate(h_times[:24]):
            hour_str = ht_str.split("T")[-1] if "T" in ht_str else ht_str[-5:]
            w_code = hourly_raw.get("weather_code", [0])[i]
            hourly_items.append({
                "time": hour_str,
                "temperature_c": round(float(hourly_raw.get("temperature_2m", [25.0])[i]), 1),
                "rain_probability": float(hourly_raw.get("precipitation_probability", [0])[i] or 0.0),
                "precipitation_mm": round(float(hourly_raw.get("precipitation", [0.0])[i]), 1),
                "humidity": round(float(hourly_raw.get("relative_humidity_2m", [55.0])[i]), 1),
                "wind_speed_kmh": round(float(hourly_raw.get("wind_speed_10m", [10.0])[i]), 1),
                "condition_text": WMO_WEATHER_CODES.get(w_code, "Partly Cloudy"),
                "weather_code": w_code
            })

        current_dict = {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": round(float(curr.get("temperature_2m", 28.0)), 1),
            "feels_like_c": round(float(curr.get("apparent_temperature", 29.5)), 1),
            "humidity": round(float(curr.get("relative_humidity_2m", 60.0)), 1),
            "wind_speed_kmh": round(float(curr.get("wind_speed_10m", 12.0)), 1),
            "wind_direction_deg": round(float(curr.get("wind_direction_10m", 180.0)), 1),
            "pressure_hpa": round(float(curr.get("surface_pressure", 1012.0)), 1),
            "visibility_km": curr_vis_km,
            "cloud_cover": round(float(curr.get("cloud_cover", 20.0)), 1),
            "rain_probability": daily_max_prob, # Today's peak rain probability for consistent daily display
            "current_rain_probability": curr_rain_prob,
            "precipitation_mm": curr_precip,
            "uv_index": uv_val,
            "sunrise": sunrise_str,
            "sunset": sunset_str,
            "condition_text": cond_curr,
            "weather_code": w_code_curr,
            "source": self.provider_name,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local")
        }

        forecast_dict = {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "source": self.provider_name,
            "confidence": "HIGH",
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local"),
            "daily": daily_items,
            "hourly": hourly_items
        }

        today_day = daily_items[0] if daily_items else {}

        facts_dict = {
            "location": location_name,
            "latitude": lat,
            "longitude": lon,
            "timezone": data.get("timezone", "auto"),
            "requested_date": today_day.get("date", datetime.date.today().strftime("%Y-%m-%d")),
            "is_current_observation": False,
            "temperature_c": current_dict["temperature_c"],
            "temp_max_c": today_day.get("temp_max_c", current_dict["temperature_c"]),
            "temp_min_c": today_day.get("temp_min_c", current_dict["temperature_c"] - 6.0),
            "feels_like_c": current_dict["feels_like_c"],
            "rain_probability": daily_max_prob,
            "daily_rain_probability_max": daily_max_prob,
            "current_rain_probability": curr_rain_prob,
            "precipitation_mm": today_day.get("precipitation_mm", curr_precip),
            "wind_speed_kmh": current_dict["wind_speed_kmh"],
            "max_wind_kmh": today_day.get("max_wind_kmh", current_dict["wind_speed_kmh"]),
            "humidity": current_dict["humidity"],
            "condition_text": cond_curr if curr_precip > 0 else today_day.get("condition_text", cond_curr),
            "weather_code": w_code_curr if curr_precip > 0 else today_day.get("weather_code", w_code_curr),
            "uv_index": uv_val,
            "source": self.provider_name,
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local"),
            "confidence": "HIGH",
            "disagreement_note": None,
            "hourly": hourly_items,
            "daily": daily_items
        }

        return {
            "current": current_dict,
            "forecast": forecast_dict,
            "facts": facts_dict
        }

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        complete = await self.fetch_complete_weather(lat, lon, location_name, days=7)
        return complete["current"]

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        complete = await self.fetch_complete_weather(lat, lon, location_name, days=days)
        return complete["forecast"]

    async def get_warnings(self, lat: float, lon: float, location_name: str) -> List[Dict[str, Any]]:
        # Return official warnings only when verified warning feed returns alerts
        return []
