import logging
import datetime
from typing import Dict, Any, List
from app.weather.base import WeatherProvider
from app.weather.open_meteo import OpenMeteoProvider
from app.weather.imd import IMDProvider
from app.weather.fallback import FallbackProvider
from app.cache.redis_client import cache_manager
from app.config import settings

logger = logging.getLogger(__name__)


class WeatherOrchestrator:

    def __init__(self):
        self.primary_provider: OpenMeteoProvider = OpenMeteoProvider()
        self.imd_provider: IMDProvider = IMDProvider()
        self.fallback_provider: FallbackProvider = FallbackProvider()
        self._last_known_weather: Dict[Any, Dict[str, Any]] = {}

    async def get_unified_weather_bundle(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        """
        Fetches or retrieves from cache the single canonical weather bundle for this coordinate.
        Both dashboard and chat consume from this exact synchronized bundle.
        """
        sanitized_loc = location_name.strip().lower()
        coord_key = (round(lat, 2), round(lon, 2))
        cache_key = f"weather:unified:{round(lat, 3)}:{round(lon, 3)}:{sanitized_loc}"

        if not settings.DEMO_MODE:
            cached = await cache_manager.get(cache_key)
            if cached:
                cached["is_cached"] = True
                return cached

        # Try live primary Open-Meteo complete fetch
        try:
            bundle = await self.primary_provider.fetch_complete_weather(lat, lon, location_name, days=max(days, 7))
            bundle["is_cached"] = False
            self._last_known_weather[coord_key] = bundle
            await cache_manager.set(cache_key, bundle, ttl_seconds=600)
            return bundle
        except Exception as e:
            logger.warning(f"Primary fetch_complete_weather failed for '{location_name}': {e}. Trying cached or IMD fallback.")
            
            # Reuse recent known good weather for this coordinate to prevent contradictory flips
            if coord_key in self._last_known_weather:
                last_bundle = self._last_known_weather[coord_key].copy()
                last_bundle["is_cached"] = True
                return last_bundle

            try:
                curr = await self.imd_provider.get_current_weather(lat, lon, location_name)
                fc = await self.imd_provider.get_forecast(lat, lon, location_name, days=days)
                daily_items = fc.get("daily", [])
                today_day = daily_items[0] if daily_items else {}
                facts = {
                    "location": location_name,
                    "latitude": lat,
                    "longitude": lon,
                    "timezone": "Asia/Kolkata",
                    "requested_date": today_day.get("date", datetime.date.today().strftime("%Y-%m-%d")),
                    "is_current_observation": False,
                    "temperature_c": curr["temperature_c"],
                    "temp_max_c": today_day.get("temp_max_c", curr["temperature_c"]),
                    "temp_min_c": today_day.get("temp_min_c", curr["temperature_c"] - 5.0),
                    "feels_like_c": curr.get("feels_like_c", curr["temperature_c"]),
                    "rain_probability": today_day.get("rain_probability", curr.get("rain_probability", 20.0)),
                    "daily_rain_probability_max": today_day.get("rain_probability", curr.get("rain_probability", 20.0)),
                    "current_rain_probability": curr.get("rain_probability", 20.0),
                    "precipitation_mm": today_day.get("precipitation_mm", 0.0),
                    "wind_speed_kmh": curr.get("wind_speed_kmh", 12.0),
                    "max_wind_kmh": today_day.get("max_wind_kmh", curr.get("wind_speed_kmh", 12.0)),
                    "humidity": curr.get("humidity", 60.0),
                    "condition_text": curr.get("condition_text", "Partly Cloudy"),
                    "weather_code": curr.get("weather_code", 2),
                    "uv_index": curr.get("uv_index", 5.0),
                    "source": self.imd_provider.provider_name,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local"),
                    "confidence": "MODERATE",
                    "disagreement_note": None,
                    "hourly": [],
                    "daily": daily_items
                }
                bundle = {"current": curr, "forecast": fc, "facts": facts, "is_cached": False}
                self._last_known_weather[coord_key] = bundle
                await cache_manager.set(cache_key, bundle, ttl_seconds=300)
                return bundle
            except Exception as e2:
                logger.error(f"IMD fallback failed: {e2}. Using demo fallback dataset.")
                curr = await self.fallback_provider.get_current_weather(lat, lon, location_name)
                fc = await self.fallback_provider.get_forecast(lat, lon, location_name, days=days)
                daily_items = fc.get("daily", [])
                today_day = daily_items[0] if daily_items else {}
                facts = {
                    "location": location_name,
                    "latitude": lat,
                    "longitude": lon,
                    "timezone": "Asia/Kolkata",
                    "requested_date": today_day.get("date", datetime.date.today().strftime("%Y-%m-%d")),
                    "is_current_observation": False,
                    "temperature_c": curr["temperature_c"],
                    "temp_max_c": today_day.get("temp_max_c", curr["temperature_c"]),
                    "temp_min_c": today_day.get("temp_min_c", curr["temperature_c"] - 6.0),
                    "feels_like_c": curr.get("feels_like_c", curr["temperature_c"]),
                    "rain_probability": today_day.get("rain_probability", curr.get("rain_probability", 20.0)),
                    "daily_rain_probability_max": today_day.get("rain_probability", curr.get("rain_probability", 20.0)),
                    "current_rain_probability": curr.get("rain_probability", 20.0),
                    "precipitation_mm": today_day.get("precipitation_mm", 0.0),
                    "wind_speed_kmh": curr.get("wind_speed_kmh", 12.0),
                    "max_wind_kmh": today_day.get("max_wind_kmh", curr.get("wind_speed_kmh", 12.0)),
                    "humidity": curr.get("humidity", 60.0),
                    "condition_text": curr.get("condition_text", "Partly Cloudy"),
                    "weather_code": curr.get("weather_code", 2),
                    "uv_index": curr.get("uv_index", 5.0),
                    "source": "WeatherGPT Backup Feed",
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M Local"),
                    "confidence": "MODERATE",
                    "disagreement_note": None,
                    "hourly": fc.get("hourly", []),
                    "daily": daily_items
                }
                return {"current": curr, "forecast": fc, "facts": facts, "is_cached": False}

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        bundle = await self.get_unified_weather_bundle(lat, lon, location_name, days=7)
        return bundle["current"]

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        bundle = await self.get_unified_weather_bundle(lat, lon, location_name, days=days)
        return bundle["forecast"]

    async def get_unified_weather_facts(self, lat: float, lon: float, location_name: str, date_offset: int = 0, is_current: bool = False) -> Dict[str, Any]:
        """
        Tailors the canonical WeatherFactSet for the exact requested horizon (current observation vs specific date).
        """
        bundle = await self.get_unified_weather_bundle(lat, lon, location_name, days=max(date_offset + 2, 7))
        base_facts = bundle["facts"].copy()
        curr_obs = bundle["current"]
        daily_list = bundle["forecast"].get("daily", [])

        if date_offset == 0:
            if is_current:
                base_facts["is_current_observation"] = True
                base_facts["date"] = "Today (Current Observation)"
                base_facts["temperature_c"] = curr_obs.get("temperature_c", base_facts.get("temperature_c", 28.0))
                base_facts["feels_like_c"] = curr_obs.get("feels_like_c", base_facts["temperature_c"])
                base_facts["wind_speed_kmh"] = curr_obs.get("wind_speed_kmh", 12.0)
                base_facts["rain_probability"] = curr_obs.get("current_rain_probability", curr_obs.get("rain_probability", base_facts.get("rain_probability", 20.0)))
                base_facts["condition_text"] = curr_obs.get("condition_text", "Partly Cloudy")
                base_facts["weather_code"] = curr_obs.get("weather_code", 2)
                base_facts["precipitation_mm"] = curr_obs.get("precipitation_mm", 0.0)
            else:
                base_facts["is_current_observation"] = False
                today_day = daily_list[0] if daily_list else {}
                base_facts["date"] = today_day.get("date", datetime.date.today().strftime("%Y-%m-%d"))
                base_facts["temperature_c"] = curr_obs.get("temperature_c", base_facts.get("temperature_c", 28.0))
                base_facts["temp_max_c"] = today_day.get("temp_max_c", curr_obs.get("temperature_c", 30.0))
                base_facts["temp_min_c"] = today_day.get("temp_min_c", curr_obs.get("temperature_c", 22.0) - 6.0)
                base_facts["rain_probability"] = today_day.get("rain_probability", base_facts.get("daily_rain_probability_max", 20.0))
                base_facts["precipitation_mm"] = today_day.get("precipitation_mm", curr_obs.get("precipitation_mm", 0.0))
                base_facts["max_wind_kmh"] = today_day.get("max_wind_kmh", curr_obs.get("wind_speed_kmh", 12.0))
                base_facts["condition_text"] = today_day.get("condition_text", curr_obs.get("condition_text", "Partly Cloudy"))
                base_facts["weather_code"] = today_day.get("weather_code", curr_obs.get("weather_code", 2))
        else:
            day_idx = min(date_offset, len(daily_list) - 1) if daily_list else 0
            target_day = daily_list[day_idx] if daily_list else {}
            base_facts["is_current_observation"] = False
            base_facts["date"] = target_day.get("date")
            base_facts["day_name"] = target_day.get("day_name")
            base_facts["temp_max_c"] = target_day.get("temp_max_c", 30.0)
            base_facts["temp_min_c"] = target_day.get("temp_min_c", 22.0)
            base_facts["temperature_c"] = target_day.get("temp_max_c", 30.0) # forecast daily representative
            base_facts["rain_probability"] = target_day.get("rain_probability", 20.0)
            base_facts["precipitation_mm"] = target_day.get("precipitation_mm", 0.0)
            base_facts["max_wind_kmh"] = target_day.get("max_wind_kmh", 12.0)
            base_facts["wind_speed_kmh"] = target_day.get("max_wind_kmh", 12.0)
            base_facts["condition_text"] = target_day.get("condition_text", "Partly Cloudy")
            base_facts["weather_code"] = target_day.get("weather_code", 2)
            base_facts["risk_level"] = target_day.get("risk_level", "LOW")

        return base_facts

    async def get_warnings(self, lat: float, lon: float, location_name: str) -> List[Dict[str, Any]]:
        sanitized_loc = location_name.strip().lower()
        cache_key = f"weather:warnings:{round(lat, 3)}:{round(lon, 3)}:{sanitized_loc}"
        cached = await cache_manager.get(cache_key)
        if cached and not settings.DEMO_MODE:
            return cached

        all_warnings = []
        try:
            p_warns = await self.primary_provider.get_warnings(lat, lon, location_name)
            all_warnings.extend(p_warns)
        except Exception:
            pass

        try:
            imd_warns = await self.imd_provider.get_warnings(lat, lon, location_name)
            all_warnings.extend(imd_warns)
        except Exception:
            pass

        if not all_warnings and settings.DEMO_MODE:
            all_warnings = await self.fallback_provider.get_warnings(lat, lon, location_name)

        await cache_manager.set(cache_key, all_warnings, ttl_seconds=300)
        return all_warnings


weather_orchestrator = WeatherOrchestrator()
