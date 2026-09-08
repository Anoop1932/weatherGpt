import asyncio
import logging
import datetime
from typing import Dict, Any, List, Optional
from app.weather.orchestrator import weather_orchestrator

logger = logging.getLogger(__name__)

from app.cache.redis_client import cache_manager

# Curated core regional stations across Indian geographical zones
REGIONAL_STATIONS = {
    "India": [
        {"name": "Delhi", "state": "Delhi", "latitude": 28.6139, "longitude": 77.2090},
        {"name": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777},
        {"name": "Kolkata", "state": "West Bengal", "latitude": 22.5726, "longitude": 88.3639},
        {"name": "Bengaluru", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946},
        {"name": "Amritsar", "state": "Punjab", "latitude": 31.6340, "longitude": 74.8723},
        {"name": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462},
        {"name": "Patna", "state": "Bihar", "latitude": 25.5941, "longitude": 85.1376},
        {"name": "Guwahati", "state": "Assam", "latitude": 26.1445, "longitude": 91.7362}
    ],
    "Punjab": [
        {"name": "Amritsar", "state": "Punjab", "latitude": 31.6340, "longitude": 74.8723},
        {"name": "Ludhiana", "state": "Punjab", "latitude": 30.9010, "longitude": 75.8573},
        {"name": "Jalandhar", "state": "Punjab", "latitude": 31.3256, "longitude": 75.5792},
        {"name": "Patiala", "state": "Punjab", "latitude": 30.3398, "longitude": 76.3869},
        {"name": "Bathinda", "state": "Punjab", "latitude": 30.2110, "longitude": 74.9455},
        {"name": "Kapurthala", "state": "Punjab", "latitude": 31.3801, "longitude": 75.3811}
    ],
    "Haryana": [
        {"name": "Gurugram", "state": "Haryana", "latitude": 28.4595, "longitude": 77.0266},
        {"name": "Hisar", "state": "Haryana", "latitude": 29.1539, "longitude": 75.7229},
        {"name": "Ambala", "state": "Haryana", "latitude": 30.3782, "longitude": 76.7767},
        {"name": "Rohtak", "state": "Haryana", "latitude": 28.8955, "longitude": 76.6066}
    ],
    "Bihar": [
        {"name": "Patna", "state": "Bihar", "latitude": 25.5941, "longitude": 85.1376},
        {"name": "Gaya", "state": "Bihar", "latitude": 24.7914, "longitude": 85.0002},
        {"name": "Muzaffarpur", "state": "Bihar", "latitude": 26.1209, "longitude": 85.3647},
        {"name": "Bhagalpur", "state": "Bihar", "latitude": 25.2425, "longitude": 87.0125}
    ],
    "Uttar Pradesh": [
        {"name": "Lucknow", "state": "Uttar Pradesh", "latitude": 26.8467, "longitude": 80.9462},
        {"name": "Varanasi", "state": "Uttar Pradesh", "latitude": 25.3176, "longitude": 82.9739},
        {"name": "Agra", "state": "Uttar Pradesh", "latitude": 27.1767, "longitude": 78.0081},
        {"name": "Kanpur", "state": "Uttar Pradesh", "latitude": 26.4499, "longitude": 80.3319}
    ]
}


async def get_regional_ranking(
    scope: str = "India",
    metric: str = "rain",
    date_offset: int = 0
) -> Dict[str, Any]:
    """
    Performs real, data-driven regional comparative analysis across sampled meteorological centers.
    Ranks locations by rainfall/precipitation or temperature with rate limiting & caching.
    """
    actual_scope = scope if scope in REGIONAL_STATIONS else (scope.title() if scope.title() in REGIONAL_STATIONS else "India")
    cache_key = f"weather:ranking:{actual_scope.lower()}:{metric}:{date_offset}"
    cached = await cache_manager.get(cache_key)
    if cached:
        return cached

    stations = REGIONAL_STATIONS.get(actual_scope, REGIONAL_STATIONS["India"])
    day_idx = max(0, min(date_offset, 6))

    sem = asyncio.Semaphore(3)

    async def fetch_station(st: Dict[str, Any]) -> Dict[str, Any]:
        async with sem:
            try:
                fc = await weather_orchestrator.get_forecast(st["latitude"], st["longitude"], st["name"], days=day_idx + 2)
                daily = fc.get("daily", [])
                target = daily[day_idx] if len(daily) > day_idx else (daily[0] if daily else {})
                return {
                    "name": st["name"],
                    "city": st["name"],
                    "state": st.get("state", actual_scope),
                    "rain_probability": float(target.get("rain_probability", 0.0)),
                    "precipitation_mm": float(target.get("precipitation_mm", 0.0)),
                    "temp_max_c": float(target.get("temp_max_c", 30.0)),
                    "temp_min_c": float(target.get("temp_min_c", 20.0)),
                    "temperature_c": float(target.get("temp_max_c", 30.0)),
                    "condition": target.get("condition_text", "Partly Cloudy"),
                    "condition_text": target.get("condition_text", "Partly Cloudy"),
                    "weather_code": target.get("weather_code", 0),
                    "date": target.get("date", datetime.date.today().strftime("%Y-%m-%d"))
                }
            except Exception as e:
                logger.warning(f"Failed to fetch forecast for {st['name']}: {e}")
                return {
                    "name": st["name"],
                    "city": st["name"],
                    "state": st.get("state", actual_scope),
                    "rain_probability": 0.0,
                    "precipitation_mm": 0.0,
                    "temp_max_c": 30.0,
                    "temp_min_c": 20.0,
                    "temperature_c": 30.0,
                    "condition": "Unavailable",
                    "condition_text": "Unavailable",
                    "weather_code": 0,
                    "date": datetime.date.today().strftime("%Y-%m-%d")
                }

    results = await asyncio.gather(*[fetch_station(st) for st in stations])

    # Sort results according to requested ranking metric
    if metric == "temperature_max":
        ranked = sorted(results, key=lambda x: x["temp_max_c"], reverse=True)
    elif metric == "temperature_min":
        ranked = sorted(results, key=lambda x: x["temp_min_c"])
    else:  # rain
        ranked = sorted(results, key=lambda x: (x["rain_probability"], x["precipitation_mm"]), reverse=True)

    target_date = ranked[0]["date"] if ranked else datetime.date.today().strftime("%Y-%m-%d")
    date_lbl = "कल (Tomorrow)" if date_offset == 1 else "आज (Today)"

    res = {
        "scope": actual_scope,
        "metric": metric,
        "date": target_date,
        "date_label": date_lbl,
        "date_offset": date_offset,
        "top_location": ranked[0] if ranked else None,
        "top_station": ranked[0] if ranked else None,
        "rankings": ranked,
        "ranking": ranked
    }
    await cache_manager.set(cache_key, res, ttl_seconds=600)
    return res
