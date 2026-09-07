import httpx
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Known Indian state & major city static lookup (ensures instant 100% reliable resolution even under API network latency)
MAJOR_INDIAN_LOCATIONS = {
    "punjab": {"name": "Ludhiana", "state": "Punjab", "country": "India", "display_name": "Punjab, India", "latitude": 30.9010, "longitude": 75.8573, "is_state": True},
    "bihar": {"name": "Patna", "state": "Bihar", "country": "India", "display_name": "Bihar, India", "latitude": 25.5941, "longitude": 85.1376, "is_state": True},
    "uttar pradesh": {"name": "Lucknow", "state": "Uttar Pradesh", "country": "India", "display_name": "Uttar Pradesh, India", "latitude": 26.8467, "longitude": 80.9462, "is_state": True},
    "haryana": {"name": "Gurugram", "state": "Haryana", "country": "India", "display_name": "Haryana, India", "latitude": 28.4595, "longitude": 77.0266, "is_state": True},
    "delhi": {"name": "New Delhi", "state": "Delhi", "country": "India", "display_name": "Delhi, India", "latitude": 28.6139, "longitude": 77.2090},
    "new delhi": {"name": "New Delhi", "state": "Delhi", "country": "India", "display_name": "New Delhi, India", "latitude": 28.6139, "longitude": 77.2090},
    "patna": {"name": "Patna", "state": "Bihar", "country": "India", "display_name": "Patna, Bihar, India", "latitude": 25.5941, "longitude": 85.1376},
    "patna, bihar": {"name": "Patna", "state": "Bihar", "country": "India", "display_name": "Patna, Bihar, India", "latitude": 25.5941, "longitude": 85.1376},
    "kapurthala": {"name": "Kapurthala", "state": "Punjab", "country": "India", "display_name": "Kapurthala, Punjab, India", "latitude": 31.3801, "longitude": 75.3811},
    "kapurthala, punjab": {"name": "Kapurthala", "state": "Punjab", "country": "India", "display_name": "Kapurthala, Punjab, India", "latitude": 31.3801, "longitude": 75.3811},
    "jalandhar": {"name": "Jalandhar", "state": "Punjab", "country": "India", "display_name": "Jalandhar, Punjab, India", "latitude": 31.3256, "longitude": 75.5792},
    "jalandhar, punjab": {"name": "Jalandhar", "state": "Punjab", "country": "India", "display_name": "Jalandhar, Punjab, India", "latitude": 31.3256, "longitude": 75.5792},
    "amritsar": {"name": "Amritsar", "state": "Punjab", "country": "India", "display_name": "Amritsar, Punjab, India", "latitude": 31.6340, "longitude": 74.8723},
    "amritsar, punjab": {"name": "Amritsar", "state": "Punjab", "country": "India", "display_name": "Amritsar, Punjab, India", "latitude": 31.6340, "longitude": 74.8723},
    "mumbai": {"name": "Mumbai", "state": "Maharashtra", "country": "India", "display_name": "Mumbai, Maharashtra, India", "latitude": 19.0760, "longitude": 72.8777},
    "bengaluru": {"name": "Bengaluru", "state": "Karnataka", "country": "India", "display_name": "Bengaluru, Karnataka, India", "latitude": 12.9716, "longitude": 77.5946},
    "kolkata": {"name": "Kolkata", "state": "West Bengal", "country": "India", "display_name": "Kolkata, West Bengal, India", "latitude": 22.5726, "longitude": 88.3639},
    "chennai": {"name": "Chennai", "state": "Tamil Nadu", "country": "India", "display_name": "Chennai, Tamil Nadu, India", "latitude": 13.0827, "longitude": 80.2707},
    "hyderabad": {"name": "Hyderabad", "state": "Telangana", "country": "India", "display_name": "Hyderabad, Telangana, India", "latitude": 17.3850, "longitude": 78.4867},
    "jaipur": {"name": "Jaipur", "state": "Rajasthan", "country": "India", "display_name": "Jaipur, Rajasthan, India", "latitude": 26.9124, "longitude": 75.7873},
    "chandigarh": {"name": "Chandigarh", "state": "Punjab", "country": "India", "display_name": "Chandigarh, India", "latitude": 30.7333, "longitude": 76.7794},
    "ludhiana": {"name": "Ludhiana", "state": "Punjab", "country": "India", "display_name": "Ludhiana, Punjab, India", "latitude": 30.9010, "longitude": 75.8573},
    "patiala": {"name": "Patiala", "state": "Punjab", "country": "India", "display_name": "Patiala, Punjab, India", "latitude": 30.3398, "longitude": 76.3869},
    "bathinda": {"name": "Bathinda", "state": "Punjab", "country": "India", "display_name": "Bathinda, Punjab, India", "latitude": 30.2110, "longitude": 74.9455},
    "shimla": {"name": "Shimla", "state": "Himachal Pradesh", "country": "India", "display_name": "Shimla, Himachal Pradesh, India", "latitude": 31.1048, "longitude": 77.1734},
    "srinagar": {"name": "Srinagar", "state": "Jammu & Kashmir", "country": "India", "display_name": "Srinagar, Jammu & Kashmir, India", "latitude": 34.0837, "longitude": 74.7973},
    "lucknow": {"name": "Lucknow", "state": "Uttar Pradesh", "country": "India", "display_name": "Lucknow, Uttar Pradesh, India", "latitude": 26.8467, "longitude": 80.9462},
    "varanasi": {"name": "Varanasi", "state": "Uttar Pradesh", "country": "India", "display_name": "Varanasi, Uttar Pradesh, India", "latitude": 25.3176, "longitude": 82.9739},
    "agra": {"name": "Agra", "state": "Uttar Pradesh", "country": "India", "display_name": "Agra, Uttar Pradesh, India", "latitude": 27.1767, "longitude": 78.0081},
    "gaya": {"name": "Gaya", "state": "Bihar", "country": "India", "display_name": "Gaya, Bihar, India", "latitude": 24.7914, "longitude": 85.0002},
    "muzaffarpur": {"name": "Muzaffarpur", "state": "Bihar", "country": "India", "display_name": "Muzaffarpur, Bihar, India", "latitude": 26.1209, "longitude": 85.3647},
    "bhagalpur": {"name": "Bhagalpur", "state": "Bihar", "country": "India", "display_name": "Bhagalpur, Bihar, India", "latitude": 25.2425, "longitude": 87.0125}
}


async def search_locations(query: str, limit: int = 10, state_hint: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Worldwide geocoding autocomplete search via Open-Meteo Geocoding API with strong Indian location ranking.
    """
    clean_query = query.strip()
    if not clean_query or len(clean_query) < 2:
        return []

    clean_lower = clean_query.lower()

    # Fast-path check for major Indian locations & states
    if clean_lower in MAJOR_INDIAN_LOCATIONS:
        return [MAJOR_INDIAN_LOCATIONS[clean_lower].copy()]

    # Handle composite queries like "Patna Bihar" or "Patna, Bihar"
    search_target = clean_query
    if "," in clean_query:
        parts = [p.strip() for p in clean_query.split(",")]
        search_target = parts[0]
        if not state_hint and len(parts) > 1:
            state_hint = parts[1]

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
                    country_code = item.get("country_code", "").upper()

                    # Scoring logic to prioritize Indian locations and correct states
                    score = 0
                    if country_code == "IN" or country.lower() == "india":
                        score += 100
                    if state_hint and state and state_hint.lower() in state.lower():
                        score += 200
                    if name.lower() == search_target.lower():
                        score += 50

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
                        "elevation": item.get("elevation", 0),
                        "score": score
                    })

                # Sort candidates by score descending
                results.sort(key=lambda x: x["score"], reverse=True)
                if results:
                    return results
    except Exception as e:
        logger.warning(f"Geocoding autocomplete search failed for '{query}': {e}")

    # Fallback to major locations lookup
    if search_target.lower() in MAJOR_INDIAN_LOCATIONS:
        return [MAJOR_INDIAN_LOCATIONS[search_target.lower()].copy()]

    return []


async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocodes lat/lon coordinates into place name, state, country.
    """
    url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
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


async def geocode_location(location_name: str, state_hint: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Resolves location name to latitude, longitude, state, country with Indian preference.
    Returns None if location is unresolvable (does NOT force Amritsar silently).
    """
    clean_name = location_name.strip()
    if not clean_name:
        return None

    from app.ai.nlp_parser import NON_LOCATION_STOPWORDS
    clean_words = clean_name.lower().split()
    if all(w in NON_LOCATION_STOPWORDS for w in clean_words):
        logger.warning(f"Geocoding rejected query '{location_name}' as non-location stopword phrase.")
        return None

    clean_lower = clean_name.lower()
    if clean_lower in MAJOR_INDIAN_LOCATIONS:
        return MAJOR_INDIAN_LOCATIONS[clean_lower].copy()

    matches = await search_locations(clean_name, limit=10, state_hint=state_hint)
    if matches:
        return matches[0]

    # Secondary attempt: ONLY if composite location (e.g. "Patna Bihar"), check if first word is a known major location
    if " " in clean_name:
        parts = clean_name.split()
        first_word = parts[0].lower()
        if first_word in MAJOR_INDIAN_LOCATIONS:
            return MAJOR_INDIAN_LOCATIONS[first_word].copy()

    return None
