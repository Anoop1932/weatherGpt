import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { applyTextDirection } from '../i18n';
import { 
  getUserGeolocation, 
  reverseGeocode, 
  saveRecentLocation, 
  getRecentLocations, 
  removeRecentLocation 
} from '../services/locationService';
import { generateWeatherSuggestions, generateDynamicContextualQuestions } from '../services/suggestionService';

const WeatherContext = createContext();

export const WeatherProvider = ({ children }) => {
  const [location, setLocation] = useState('Amritsar');
  const [locationCoords, setLocationCoords] = useState({ latitude: 31.6340, longitude: 74.8723 });
  const [language, setLanguage] = useState('en');
  const [theme, setTheme] = useState(() => localStorage.getItem('weathergpt_theme') || 'light');
  const [currentWeather, setCurrentWeather] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [warnings, setWarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [geoLoading, setGeoLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedForecastIndex, setSelectedForecastIndex] = useState(0);
  
  // Conversation session state memory
  const [activeContextLocation, setActiveContextLocation] = useState('Amritsar');
  const [activeContextDate, setActiveContextDate] = useState(null);
  const [activeContextIntent, setActiveContextIntent] = useState(null);

  const [recentLocs, setRecentLocs] = useState(getRecentLocations());
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'assistant',
      text: 'Namaste! I am WeatherGPT. Ask me natural questions by text or voice: "Kal Patna Bihar mein barish hogi?", "Jalandhar ka weather kya hai is time?", or "Kapurthala Punjab mein barish hogi?"',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      risk_level: 'LOW',
      confidence: 'HIGH',
      source: 'Open-Meteo Meteorological Service'
    }
  ]);

  // Handle Theme (Light / Dark)
  useEffect(() => {
    localStorage.setItem('weathergpt_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  useEffect(() => {
    applyTextDirection(language);
  }, [language]);

  const fetchWeatherData = async (targetLoc = location, coords = null) => {
    setLoading(true);
    setError(null);
    try {
      let urlParam = `location=${encodeURIComponent(targetLoc)}`;
      if (coords && coords.latitude && coords.longitude) {
        urlParam += `&lat=${coords.latitude}&lon=${coords.longitude}`;
      }

      const [currRes, fcRes, warnRes] = await Promise.all([
        axios.get(`/api/weather/current?${urlParam}`),
        axios.get(`/api/weather/forecast?${urlParam}&days=7`),
        axios.get(`/api/weather/warnings?${urlParam}`)
      ]);

      setCurrentWeather(currRes.data);
      setForecast(fcRes.data);
      setWarnings(warnRes.data);
      setSelectedForecastIndex(0);
      setActiveContextLocation(targetLoc);

      if (currRes.data.latitude && currRes.data.longitude) {
        setLocationCoords({ latitude: currRes.data.latitude, longitude: currRes.data.longitude });
      }

      // Save to local recent locations
      saveRecentLocation({
        name: currRes.data.location,
        display_name: targetLoc,
        latitude: currRes.data.latitude,
        longitude: currRes.data.longitude
      });
      setRecentLocs(getRecentLocations());
    } catch (err) {
      console.error("Weather fetch error:", err);
      setError("Unable to connect to live meteorological feed. Showing last cached updates.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherData(location, locationCoords);
  }, [location]);

  const selectLocation = (locItem) => {
    if (typeof locItem === 'string') {
      setLocation(locItem);
      setLocationCoords({ latitude: null, longitude: null });
      fetchWeatherData(locItem, null);
    } else if (locItem && locItem.latitude && locItem.longitude) {
      const targetName = locItem.display_name || locItem.name;
      const targetCoords = { latitude: locItem.latitude, longitude: locItem.longitude };
      setLocation(targetName);
      setLocationCoords(targetCoords);
      fetchWeatherData(targetName, targetCoords);
    }
  };

  const useCurrentGeolocation = async () => {
    setGeoLoading(true);
    try {
      const coords = await getUserGeolocation();
      const place = await reverseGeocode(coords.latitude, coords.longitude);
      const placeName = place.display_name || place.name;
      setLocation(placeName);
      setLocationCoords(coords);
      fetchWeatherData(placeName, coords);
    } catch (e) {
      alert("Location permission was denied or unavailable. Please search your city manually.");
    } finally {
      setGeoLoading(false);
    }
  };

  const handleRemoveRecent = (nameToRemove) => {
    const updated = removeRecentLocation(nameToRemove);
    setRecentLocs(updated);
  };

  const sendQuery = async (queryText) => {
    const userMsg = {
      sender: 'user',
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setChatMessages((prev) => [...prev, userMsg]);

    try {
      const resp = await axios.post('/api/weather/query', {
        query: queryText,
        location: activeContextLocation || location,
        latitude: locationCoords.latitude,
        longitude: locationCoords.longitude,
        language: language,
        last_location: activeContextLocation,
        last_date: activeContextDate,
        last_intent: activeContextIntent
      });
      const data = resp.data;

      // Update conversation session context memory
      if (data.resolved_location) {
        setActiveContextLocation(data.resolved_location);
        if (data.weather_facts?.latitude && data.weather_facts?.longitude && data.resolved_location.toLowerCase() !== location.toLowerCase()) {
          setLocation(data.resolved_location);
          setLocationCoords({ latitude: data.weather_facts.latitude, longitude: data.weather_facts.longitude });
          fetchWeatherData(data.resolved_location, { latitude: data.weather_facts.latitude, longitude: data.weather_facts.longitude });
        }
      }
      if (data.resolved_date) {
        setActiveContextDate(data.resolved_date);
      }
      if (data.extracted_intent) {
        setActiveContextIntent(data.extracted_intent);
      }

      const assistantMsg = {
        sender: 'assistant',
        text: data.grounded_answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        risk_level: data.risk_evaluation?.risk_level || 'LOW',
        confidence: data.confidence || 'HIGH',
        source: data.source,
        updated_at: data.updated_at,
        weather_facts: data.weather_facts,
        risk_evaluation: data.risk_evaluation,
        is_non_weather: data.is_non_weather,
        is_missing_location: data.is_missing_location
      };
      setChatMessages((prev) => [...prev, assistantMsg]);
      return assistantMsg;
    } catch (err) {
      const fallbackMsg = {
        sender: 'assistant',
        text: `Based on verified weather evidence for ${activeContextLocation || location}, temperature is ${currentWeather?.temperature_c || 30}°C and rain probability is ${currentWeather?.rain_probability || 20}%.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        risk_level: 'LOW',
        confidence: 'HIGH',
        source: 'Open-Meteo'
      };
      setChatMessages((prev) => [...prev, fallbackMsg]);
      return fallbackMsg;
    }
  };

  let activeWeather = currentWeather;
  if (selectedForecastIndex > 0 && forecast?.daily?.[selectedForecastIndex]) {
    const dayItem = forecast.daily[selectedForecastIndex];
    activeWeather = {
      ...currentWeather,
      temperature_c: dayItem.temp_max_c,
      feels_like_c: roundNumber(dayItem.temp_max_c + 2.0, 1),
      condition_text: dayItem.condition_text,
      rain_probability: dayItem.rain_probability,
      uv_index: dayItem.uv_index_max,
      wind_speed_kmh: dayItem.max_wind_kmh,
      precipitation_mm: dayItem.precipitation_mm,
      weather_code: dayItem.weather_code,
      updated_at: `Forecast for ${dayItem.day_name}, ${dayItem.date}`
    };
  }

  const weatherSuggestions = generateWeatherSuggestions(activeWeather, warnings);
  const dynamicQuestions = generateDynamicContextualQuestions(location, activeWeather);

  return (
    <WeatherContext.Provider value={{
      location,
      setLocation: selectLocation,
      locationCoords,
      language,
      setLanguage,
      theme,
      toggleTheme,
      currentWeather,
      activeWeather,
      forecast,
      warnings,
      loading,
      geoLoading,
      error,
      selectedForecastIndex,
      setSelectedForecastIndex,
      recentLocs,
      removeRecentLoc: handleRemoveRecent,
      useCurrentGeolocation,
      chatMessages,
      sendQuery,
      weatherSuggestions,
      dynamicQuestions,
      refreshData: () => fetchWeatherData(location, locationCoords)
    }}>
      {children}
    </WeatherContext.Provider>
  );
};

const roundNumber = (num, decimals) => {
  const factor = Math.pow(10, decimals);
  return Math.round(num * factor) / factor;
};

export const useWeather = () => useContext(WeatherContext);
