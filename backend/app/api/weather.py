import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from app.weather.orchestrator import weather_orchestrator
from app.utils.geocoding import geocode_location, search_locations, reverse_geocode
from app.schemas.weather_schemas import CurrentWeatherResponse, ForecastResponse, WarningItem, HistoricalWeatherItem

router = APIRouter(prefix="/weather", tags=["Weather Intelligence"])


@router.get("/locations/search", response_model=List[Dict[str, Any]])
async def autocomplete_locations(
    q: str = Query(..., min_length=2, description="Search query string"),
    limit: int = Query(8, ge=1, le=15)
):
    try:
        return await search_locations(q, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Location autocomplete failed: {str(e)}")


@router.get("/locations/reverse", response_model=Dict[str, Any])
async def reverse_geocode_location(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    try:
        return await reverse_geocode(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse geocoding failed: {str(e)}")


@router.get("/current", response_model=CurrentWeatherResponse)
async def get_current_weather(
    location: Optional[str] = Query("Amritsar", description="Location city or district name"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude")
):
    try:
        if lat is None or lon is None:
            geo = await geocode_location(location)
            lat, lon = geo["latitude"], geo["longitude"]
            location = geo.get("display_name") or geo["name"]

        data = await weather_orchestrator.get_current_weather(lat, lon, location)
        return CurrentWeatherResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current weather: {str(e)}")


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    location: Optional[str] = Query("Amritsar", description="Location name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    days: int = Query(7, ge=1, le=14)
):
    try:
        if lat is None or lon is None:
            geo = await geocode_location(location)
            lat, lon = geo["latitude"], geo["longitude"]
            location = geo.get("display_name") or geo["name"]

        data = await weather_orchestrator.get_forecast(lat, lon, location, days)
        return ForecastResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather forecast: {str(e)}")


@router.get("/warnings", response_model=List[WarningItem])
async def get_warnings(
    location: Optional[str] = Query("Amritsar"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    try:
        if lat is None or lon is None:
            geo = await geocode_location(location)
            lat, lon = geo["latitude"], geo["longitude"]
            location = geo.get("display_name") or geo["name"]

        warns = await weather_orchestrator.get_warnings(lat, lon, location)
        return [WarningItem(**w) for w in warns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather warnings: {str(e)}")


@router.get("/historical", response_model=List[HistoricalWeatherItem])
async def get_historical(
    location: str = Query("Amritsar"),
    days: int = Query(7, ge=1, le=30)
):
    today = datetime.date.today()
    result = []
    for i in range(1, days + 1):
        dt = today - datetime.timedelta(days=i)
        result.append(HistoricalWeatherItem(
            date=dt.strftime("%Y-%m-%d"),
            max_temp_c=round(31.5 + (i % 3) - 1, 1),
            min_temp_c=round(21.0 + (i % 2), 1),
            precipitation_mm=round(8.5 if i in [2, 5] else 0.0, 1),
            max_wind_kmh=round(14.0 + i, 1),
            condition="Rain Showers" if i in [2, 5] else "Clear"
        ))
    return result
