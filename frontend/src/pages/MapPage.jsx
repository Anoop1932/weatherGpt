import React from 'react';
import WeatherMap from '../components/WeatherMap';

export const MapPage = () => {
  return (
    <div className="space-y-4 pb-12 h-[calc(100vh-120px)] flex flex-col text-slate-900">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Weather Radar & Location Map</h2>
        <p className="text-xs text-slate-600 mt-1">Explore live weather station coordinates, temperature markers, and regional map parameters.</p>
      </div>

      <div className="flex-1">
        <WeatherMap />
      </div>
    </div>
  );
};

export default MapPage;
