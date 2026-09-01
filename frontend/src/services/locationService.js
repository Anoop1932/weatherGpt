import axios from 'axios';

const RECENT_LOCATIONS_KEY = 'weathergpt_recent_locations';

export const searchLocations = async (query) => {
  if (!query || query.trim().length < 2) return [];
  try {
    const resp = await axios.get(`/api/weather/locations/search?q=${encodeURIComponent(query.trim())}`);
    return resp.data || [];
  } catch (err) {
    console.error("Location search API error:", err);
    return [];
  }
};

export const reverseGeocode = async (lat, lon) => {
  try {
    const resp = await axios.get(`/api/weather/locations/reverse?lat=${lat}&lon=${lon}`);
    return resp.data;
  } catch (err) {
    console.error("Reverse geocoding error:", err);
    return { name: `Location [${round(lat,2)}, ${round(lon,2)}]`, latitude: lat, longitude: lon };
  }
};

export const getUserGeolocation = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Browser Geolocation is not supported."));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        });
      },
      (error) => {
        reject(error);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  });
};

export const getRecentLocations = () => {
  try {
    const stored = localStorage.getItem(RECENT_LOCATIONS_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (e) {
    return [];
  }
};

export const saveRecentLocation = (locObj) => {
  try {
    if (!locObj || !locObj.name) return;
    const current = getRecentLocations();
    // Filter out duplicate by display_name or name
    const filtered = current.filter(
      (item) => (item.display_name || item.name).toLowerCase() !== (locObj.display_name || locObj.name).toLowerCase()
    );
    const updated = [locObj, ...filtered].slice(0, 5); // Keep top 5
    localStorage.setItem(RECENT_LOCATIONS_KEY, JSON.stringify(updated));
  } catch (e) {
    console.error("Failed to save recent location:", e);
  }
};

export const removeRecentLocation = (nameToRemove) => {
  try {
    const current = getRecentLocations();
    const filtered = current.filter(
      (item) => (item.display_name || item.name).toLowerCase() !== nameToRemove.toLowerCase()
    );
    localStorage.setItem(RECENT_LOCATIONS_KEY, JSON.stringify(filtered));
    return filtered;
  } catch (e) {
    return [];
  }
};
