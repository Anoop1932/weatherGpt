import React from 'react';
import { useWeather } from '../context/WeatherContext';
import ForecastChart from '../components/ForecastChart';
import RiskBadge from '../components/RiskBadge';
import { CalendarDays, CloudRain, Wind, Sun } from 'lucide-react';

export const Forecast = () => {
  const { forecast, location } = useWeather();
  const dailyList = forecast?.daily || [];

  return (
    <div className="space-y-6 pb-12 text-slate-900">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Detailed Weather Forecast — {location}</h2>
          <p className="text-xs text-slate-600 mt-1">7-Day meteorological forecast sequence</p>
        </div>
      </div>

      <ForecastChart />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dailyList.map((day, idx) => (
          <div key={idx} className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-base font-bold text-slate-900">{day.day_name}</h4>
                <p className="text-xs text-slate-500 font-medium">{day.date}</p>
              </div>
              <RiskBadge level={day.risk_level} />
            </div>

            <div className="flex items-center gap-3 py-2 border-y border-slate-100">
              <Sun className="w-8 h-8 text-amber-500 shrink-0" />
              <div>
                <div className="text-2xl font-extrabold text-slate-900">{day.temp_max_c}° / {day.temp_min_c}°C</div>
                <div className="text-xs text-slate-700 font-medium">{day.condition_text}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
              <div className="flex items-center gap-1.5">
                <CloudRain className="w-3.5 h-3.5 text-sky-600" />
                <span>Rain: <strong className="text-slate-900 font-semibold">{day.rain_probability}%</strong></span>
              </div>
              <div className="flex items-center gap-1.5">
                <Wind className="w-3.5 h-3.5 text-emerald-600" />
                <span>Wind: <strong className="text-slate-900 font-semibold">{day.max_wind_kmh} km/h</strong></span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Forecast;
