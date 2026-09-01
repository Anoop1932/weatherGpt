import React, { useState } from 'react';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { Thermometer, CloudRain, Wind } from 'lucide-react';

export const ForecastChart = () => {
  const { forecast, language, location } = useWeather();
  const [activeMetric, setActiveMetric] = useState('temp');

  if (!forecast || !forecast.hourly || forecast.hourly.length === 0) {
    return (
      <div className="bg-white border border-slate-200 shadow-sm rounded-3xl p-6 h-64 flex items-center justify-center text-slate-400 text-xs">
        Fetching live hourly forecast trends for {location}...
      </div>
    );
  }

  // Pick next 24 hours of real API data
  const chartData = forecast.hourly.slice(0, 24);

  return (
    <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-6 space-y-4 text-slate-900">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
        <div>
          <h3 className="font-heading text-lg font-bold text-slate-900 tracking-tight">
            Hourly Meteorological Trends
          </h3>
          <p className="text-xs text-slate-500">Live forecast sequence for {location}</p>
        </div>

        {/* Metric Switcher Tabs */}
        <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
          <button
            type="button"
            onClick={() => setActiveMetric('temp')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition font-medium ${
              activeMetric === 'temp'
                ? 'bg-white text-amber-600 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Thermometer className="w-3.5 h-3.5" />
            <span>Temperature</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveMetric('rain')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition font-medium ${
              activeMetric === 'rain'
                ? 'bg-white text-sky-600 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <CloudRain className="w-3.5 h-3.5" />
            <span>Rain Prob %</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveMetric('wind')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition font-medium ${
              activeMetric === 'wind'
                ? 'bg-white text-emerald-600 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Wind className="w-3.5 h-3.5" />
            <span>Wind</span>
          </button>
        </div>
      </div>

      <div className="h-64 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          {activeMetric === 'temp' ? (
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="tempGradientLight" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#d97706" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#d97706" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  color: '#0f172a',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(val) => [`${val}°C`, 'Temperature']}
              />
              <Area
                type="monotone"
                dataKey="temperature_c"
                name="Temperature (°C)"
                stroke="#d97706"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#tempGradientLight)"
              />
            </AreaChart>
          ) : activeMetric === 'rain' ? (
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  color: '#0f172a',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(val) => [`${val}%`, 'Precipitation Probability']}
              />
              <Bar
                dataKey="rain_probability"
                name="Rain Prob (%)"
                fill="#0284c7"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          ) : (
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="windGradientLight" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#059669" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  borderColor: '#e2e8f0',
                  borderRadius: '0.75rem',
                  color: '#0f172a',
                  fontSize: '12px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(val) => [`${val} km/h`, 'Wind Speed']}
              />
              <Area
                type="monotone"
                dataKey="wind_speed_kmh"
                name="Wind Speed (km/h)"
                stroke="#059669"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#windGradientLight)"
              />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ForecastChart;
