import httpx
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


STATE_MAP = {
    "up": "Uttar Pradesh",
    "uttar pradesh": "Uttar Pradesh",
    "pb": "Punjab",
    "punjab": "Punjab",
    "hr": "Haryana",
    "haryana": "Haryana",
    "dl": "Delhi",
    "delhi": "Delhi",
    "uk": "Uttarakhand",
    "uttarakhand": "Uttarakhand",
    "mp": "Madhya Pradesh",
    "madhya pradesh": "Madhya Pradesh",
    "hp": "Himachal Pradesh",
    "himachal pradesh": "Himachal Pradesh",
    "mh": "Maharashtra",
    "maharashtra": "Maharashtra",
    "wb": "West Bengal",
    "west bengal": "West Bengal",
    "tn": "Tamil Nadu",
    "tamil nadu": "Tamil Nadu",
    "ka": "Karnataka",
    "karnataka": "Karnataka",
    "kl": "Kerala",
    "kerala": "Kerala",
    "ap": "Andhra Pradesh",
    "andhra pradesh": "Andhra Pradesh",
    "ts": "Telangana",
    "tg": "Telangana",
    "telangana": "Telangana",
    "rj": "Rajasthan",
    "rajasthan": "Rajasthan",
    "gj": "Gujarat",
    "gujarat": "Gujarat",
    "bombay": "Mumbai",
    "calcutta": "Kolkata",
    "madras": "Chennai",
    "bangalore": "Bengaluru",
    "benares": "Varanasi",
    "banaras": "Varanasi"
}


async def search_locations(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Worldwide geocoding autocomplete search via Open-Meteo Geocoding API.
    Resolves countries, states, districts, cities, towns, villages, and localities.
    """
    clean_query = query.strip()
    if not clean_query or len(clean_query) < 2:
        return []

    # Pre-process query for state abbreviations & synonyms
    query_lower = clean_query.lower()
    if query_lower in STATE_MAP:
        search_target = STATE_MAP[query_lower]
    else:
        search_target = clean_query

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": search_target,
        "count": min(limit, 10),
        "language": "en",
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("results", []):
                    name = item.get("name", "")
                    state = item.get("admin1", item.get("admin2", ""))
                    country = item.get("country", "")
                    country_code = item.get("country_code", "")

                    # Construct readable location string
                    display_parts = [name]
                    if state and state.lower() != name.lower():
                        display_parts.append(state)
                    if country:
                        display_parts.append(country)

                    display_name = ", ".join(display_parts)

                    results.append({
                        "name": name,
                        "state": state,
                        "country": country,
                        "country_code": country_code,
                        "display_name": display_name,
                        "latitude": round(float(item["latitude"]), 4),
                        "longitude": round(float(item["longitude"]), 4),
                        "elevation": item.get("elevation", 0)
                    })
                return results
    except Exception as e:
        logger.warning(f"Geocoding autocomplete search failed for '{query}': {e}")

    return []


async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocodes lat/lon coordinates into place name, state, country.
    """
    url = f"https://api.bigdatacloud.net/data/reverse-geocode-client"
    params = {"latitude": lat, "longitude": lon, "localityLanguage": "en"}

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                city = data.get("city") or data.get("locality") or data.get("principalSubdivision") or "Current Location"
                state = data.get("principalSubdivision", "")
                country = data.get("countryName", "India")
                return {
                    "name": city,
                    "state": state,
                    "country": country,
                    "display_name": f"{city}, {state}, {country}" if state else f"{city}, {country}",
                    "latitude": round(lat, 4),
                    "longitude": round(lon, 4)
                }
    except Exception as e:
        logger.warning(f"Reverse geocoding failed for {lat}, {lon}: {e}")

    return {
        "name": "Current Location",
        "state": "",
        "country": "India",
        "display_name": f"Current Location [{round(lat,2)}, {round(lon,2)}]",
        "latitude": round(lat, 4),
        "longitude": round(lon, 4)
    }


async def geocode_location(location_name: str) -> Dict[str, Any]:
    """
    Resolves location name to latitude, longitude, state, country.
    """
    clean_name = location_name.strip()
    clean_lower = clean_name.lower()

    if clean_lower in STATE_MAP:
        clean_name = STATE_MAP[clean_lower]

    matches = await search_locations(clean_name, limit=1)
    if matches:
        return matches[0]

    # Default fallback to Amritsar if unresolvable
    return {
        "name": "Amritsar",
        "state": "Punjab",
        "country": "India",
        "display_name": "Amritsar, Punjab, India",
        "latitude": 31.6340,
        "longitude": 74.8723
    }

