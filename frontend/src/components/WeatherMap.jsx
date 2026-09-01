import React, { useEffect, useRef } from 'react';
import { useWeather } from '../context/WeatherContext';
import { reverseGeocode } from '../services/locationService';
import L from 'leaflet';

export const WeatherMap = () => {
  const { currentWeather, setLocation } = useWeather();
  const mapRef = useRef(null);
  const leafletMap = useRef(null);

  const lat = currentWeather?.latitude || 31.6340;
  const lon = currentWeather?.longitude || 74.8723;
  const locName = currentWeather?.location || 'Amritsar';
  const temp = currentWeather?.temperature_c || 31.0;
  const condition = currentWeather?.condition_text || 'Partly Cloudy';

  const handleMapClick = async (e) => {
    const clickedLat = Math.round(e.latlng.lat * 10000) / 10000;
    const clickedLon = Math.round(e.latlng.lng * 10000) / 10000;
    try {
      const place = await reverseGeocode(clickedLat, clickedLon);
      const placeName = place.display_name || place.name || `Loc [${clickedLat}, ${clickedLon}]`;
      setLocation({
        name: place.name || placeName,
        display_name: placeName,
        latitude: clickedLat,
        longitude: clickedLon
      });
    } catch (err) {
      console.error("Map click location resolution failed:", err);
    }
  };

  useEffect(() => {
    if (!mapRef.current) return;

    if (!leafletMap.current) {
      // Initialize Leaflet map
      const map = L.map(mapRef.current, {
        center: [lat, lon],
        zoom: 10,
        zoomControl: true,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      map.on('click', handleMapClick);

      leafletMap.current = map;
    } else {
      leafletMap.current.setView([lat, lon], leafletMap.current.getZoom() || 10);
    }

    // Clear existing markers
    leafletMap.current.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        leafletMap.current.removeLayer(layer);
      }
    });

    // Custom Marker
    const customIcon = L.divIcon({
      className: 'custom-weather-marker',
      html: `
        <div style="background: #ffffff; border: 2px solid #0284c7; color: #0f172a; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 12px; white-space: nowrap; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
          📍 ${locName}: ${temp}°C
        </div>
      `,
      iconSize: [140, 36],
      iconAnchor: [70, 18]
    });

    const marker = L.marker([lat, lon], { icon: customIcon }).addTo(leafletMap.current);
    marker.bindPopup(`
      <div style="font-family: sans-serif; color: #0F172A; padding: 4px;">
        <h4 style="margin: 0; font-size: 14px; font-weight: bold;">${locName}</h4>
        <p style="margin: 4px 0 0 0; font-size: 12px;">Temperature: <strong>${temp}°C</strong></p>
        <p style="margin: 2px 0 0 0; font-size: 12px;">Condition: <strong>${condition}</strong></p>
        <p style="margin: 4px 0 0 0; font-size: 10px; color: #0284c7;">Click anywhere on map to change location</p>
      </div>
    `);

  }, [lat, lon, locName, temp, condition]);

  return (
    <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 flex flex-col h-full min-h-[380px] text-slate-900">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 tracking-tight">Weather Map & Radar</h3>
          <p className="text-[11px] text-slate-500">Click anywhere on the map to fetch live location weather</p>
        </div>
        <span className="text-xs text-sky-700 font-semibold bg-sky-50 px-2.5 py-1 rounded-lg border border-sky-100">{locName} [{lat}, {lon}]</span>
      </div>
      <div ref={mapRef} className="w-full h-full min-h-[320px] rounded-2xl overflow-hidden border border-slate-200 cursor-pointer"></div>
    </div>
  );
};

export default WeatherMap;

