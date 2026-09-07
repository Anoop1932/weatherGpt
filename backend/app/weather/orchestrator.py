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
        self.primary_provider: WeatherProvider = OpenMeteoProvider()
        self.imd_provider: WeatherProvider = IMDProvider()
        self.fallback_provider: WeatherProvider = FallbackProvider()

    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        sanitized_loc = location_name.strip().lower()
        cache_key = f"weather:current:{round(lat, 3)}:{round(lon, 3)}:{sanitized_loc}"
        
        # Check cache unless DEMO_MODE forces fresh
        if not settings.DEMO_MODE:
            cached = await cache_manager.get(cache_key)
            if cached:
                cached["is_cached"] = True
                return cached

        # DEMO_MODE quick branch
        if settings.DEMO_MODE:
            res = await self.fallback_provider.get_current_weather(lat, lon, location_name)
            await cache_manager.set(cache_key, res, ttl_seconds=600)
            return res

        # Try live primary provider
        try:
            res = await self.primary_provider.get_current_weather(lat, lon, location_name)
            res["is_cached"] = False
            await cache_manager.set(cache_key, res, ttl_seconds=600)
            return res
        except Exception as e:
            logger.error(f"Primary weather provider failed: {e}. Trying IMD Provider...")
            try:
                res = await self.imd_provider.get_current_weather(lat, lon, location_name)
                res["is_cached"] = False
                await cache_manager.set(cache_key, res, ttl_seconds=300)
                return res
            except Exception as e2:
                logger.error(f"IMD Provider failed: {e2}. Reverting to fallback provider.")
                res = await self.fallback_provider.get_current_weather(lat, lon, location_name)
                res["is_cached"] = False
                return res

    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        sanitized_loc = location_name.strip().lower()
        cache_key = f"weather:forecast:{round(lat, 3)}:{round(lon, 3)}:{sanitized_loc}:{days}"

        if not settings.DEMO_MODE:
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached

        if settings.DEMO_MODE:
            res = await self.fallback_provider.get_forecast(lat, lon, location_name, days)
            await cache_manager.set(cache_key, res, ttl_seconds=600)
            return res

        primary_fc = None
        imd_fc = None

        try:
            primary_fc = await self.primary_provider.get_forecast(lat, lon, location_name, days)
        except Exception as e:
            logger.error(f"Primary forecast failed: {e}")

        try:
            imd_fc = await self.imd_provider.get_forecast(lat, lon, location_name, days)
        except Exception as e:
            logger.error(f"IMD forecast failed: {e}")

        if not primary_fc and not imd_fc:
            logger.warning("All forecast APIs failed. Using fallback dataset.")
            return await self.fallback_provider.get_forecast(lat, lon, location_name, days)

        final_fc = primary_fc or imd_fc

        # Evaluate multi-source disagreement heuristic if both available
        confidence = "HIGH"
        disagreement_note = None

        if primary_fc and imd_fc and len(primary_fc.get("daily", [])) > 1 and len(imd_fc.get("daily", [])) > 1:
            p_prob = primary_fc["daily"][1].get("rain_probability", 0)
            imd_prob = imd_fc["daily"][1].get("rain_probability", 0)
            diff = abs(p_prob - imd_prob)

            if diff > 25:
                confidence = "MODERATE"
                disagreement_note = (
                    f"Forecast confidence is MODERATE due to model disagreement for tomorrow: "
                    f"Open-Meteo predicts {p_prob}% rain probability vs IMD bulletin estimate of {imd_prob}%."
                )
            elif diff > 40:
                confidence = "LOW"
                disagreement_note = (
                    f"Forecast confidence is LOW due to significant source variance: "
                    f"Open-Meteo ({p_prob}%) vs IMD ({imd_prob}%)."
                )

        final_fc["confidence"] = confidence
        final_fc["disagreement_note"] = disagreement_note

        await cache_manager.set(cache_key, final_fc, ttl_seconds=600)
        return final_fc

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
