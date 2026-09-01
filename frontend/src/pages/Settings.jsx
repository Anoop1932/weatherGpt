import React from 'react';
import { useWeather } from '../context/WeatherContext';
import { Settings as SettingsIcon, Globe, MapPin, Cpu } from 'lucide-react';

export const Settings = () => {
  const { location, setLocation, language, setLanguage } = useWeather();

  return (
    <div className="space-y-6 pb-12 max-w-3xl text-slate-900">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-sky-600" />
          System & Preference Settings
        </h2>
        <p className="text-xs text-slate-600 mt-1">Configure default location, language preferences, and provider parameters</p>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-sky-600" /> Default Location
          </label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-sky-500 focus:bg-white transition"
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Globe className="w-4 h-4 text-sky-600" /> Primary Language
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 text-slate-900 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-sky-500 focus:bg-white transition"
          >
            <option value="en">English (Global)</option>
            <option value="hi">हिंदी (Hindi / Hinglish)</option>
            <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
          </select>
        </div>

        <div className="pt-4 border-t border-slate-100 space-y-3">
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-600" /> Provider Pipeline Status
          </h4>
          <div className="text-xs text-slate-600 space-y-1.5 font-medium">
            <div className="flex justify-between"><span>Primary Weather API:</span><strong className="text-emerald-700 font-semibold">Open-Meteo Service (Active)</strong></div>
            <div className="flex justify-between"><span>Official Watch Bulletin:</span><strong className="text-sky-700 font-semibold">IMD RMC Adapter (Active)</strong></div>
            <div className="flex justify-between"><span>Deterministic Risk Engine:</span><strong className="text-emerald-700 font-semibold">Verified Thresholds Active</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
