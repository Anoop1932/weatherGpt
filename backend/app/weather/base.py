from abc import ABC, abstractmethod
from typing import Dict, Any, List


class WeatherProvider(ABC):
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the meteorological data provider."""
        pass

    @abstractmethod
    async def get_current_weather(self, lat: float, lon: float, location_name: str) -> Dict[str, Any]:
        """Fetches current weather observations."""
        pass

    @abstractmethod
    async def get_forecast(self, lat: float, lon: float, location_name: str, days: int = 7) -> Dict[str, Any]:
        """Fetches hourly and daily weather forecasts."""
        pass

    @abstractmethod
    async def get_warnings(self, lat: float, lon: float, location_name: str) -> List[Dict[str, Any]]:
        """Fetches severe weather warnings and alerts for the location."""
        pass
