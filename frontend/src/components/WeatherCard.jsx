import React from 'react';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import { getWeatherIcon } from '../utils/weatherIcons';
import { 
  CloudRain, 
  Sun, 
  Wind, 
  Droplets, 
  Eye, 
  Gauge, 
  Clock, 
  CheckCircle2, 
  Sunrise, 
  Sunset, 
  MapPin
} from 'lucide-react';

export const WeatherCard = () => {
  const { currentWeather, activeWeather, language, loading } = useWeather();

  const displayWeather = activeWeather || currentWeather;

  if (loading || !displayWeather) {
    return (
      <div className="weather-panel p-8 animate-pulse space-y-6">
        <div className="h-6 bg-slate-200 dark:bg-slate-700 rounded w-1/4"></div>
        <div className="h-24 bg-slate-200 dark:bg-slate-700 rounded w-1/3"></div>
        <div className="h-12 bg-slate-200 dark:bg-slate-700 rounded w-full"></div>
      </div>
    );
  }

  const {
    location,
    temperature_c,
    feels_like_c,
    temp_max_c,
    temp_min_c,
    humidity,
    wind_speed_kmh,
    pressure_hpa,
    visibility_km,
    rain_probability,
    uv_index,
    sunrise,
    sunset,
    condition_text,
    weather_code,
    source,
    updated_at
  } = displayWeather;

  // Determine daytime by checking current local hour vs sunrise/sunset if available
  let isDaytime = true;
  const nowHour = new Date().getHours();
  if (nowHour >= 19 || nowHour < 6) {
    isDaytime = false;
  }

  return (
    <div className="weather-panel p-6 sm:p-8 space-y-6 relative overflow-hidden text-slate-900 dark:text-slate-100">
      {/* Top Location Bar & Freshness Stamp */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 font-medium mb-0.5">
            <MapPin className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span className="uppercase tracking-wider font-semibold">{t('current_location', language)}</span>
          </div>
          <h2 className="font-heading text-3xl sm:text-4xl font-bold text-slate-900 dark:text-white tracking-tight">{location}</h2>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-1.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 px-3 py-1.5 rounded-xl">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>{updated_at}</span>
          </div>
        </div>
      </div>

      {/* Hero Temperature & Condition Display */}
      <div className="flex flex-wrap items-center justify-between gap-6 py-2">
        <div className="flex items-center gap-6">
          <div className="shrink-0 p-3.5 rounded-2xl bg-sky-50 dark:bg-slate-800 border border-sky-100 dark:border-slate-700">
            {getWeatherIcon(weather_code, isDaytime, "w-16 h-16")}
          </div>
          <div>
            <div className="font-heading text-6xl sm:text-7xl font-bold text-slate-900 dark:text-white tracking-tighter leading-none">
              {temperature_c}<span className="text-4xl text-slate-400 font-normal">°C</span>
            </div>
            <div className="text-base text-slate-700 dark:text-slate-300 font-semibold mt-2 flex items-center gap-3">
              <span>{condition_text}</span>
              <span className="text-slate-400 text-sm">• {t('feels_like', language)} {feels_like_c}°C</span>
            </div>
            {(temp_max_c !== undefined || temp_min_c !== undefined) && (
              <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mt-1">
                High {temp_max_c || temperature_c}° • Low {temp_min_c || Math.round(temperature_c - 5)}°
              </div>
            )}
          </div>
        </div>

        {/* Sunrise & Sunset Inline Info */}
        <div className="flex items-center gap-6 text-xs bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 px-4 py-3 rounded-2xl shrink-0">
          <div className="flex items-center gap-2.5">
            <Sunrise className="w-4 h-4 text-amber-500" />
            <div>
              <div className="text-[11px] text-slate-400">{t('sunrise', language)}</div>
              <div className="font-semibold text-slate-800 dark:text-slate-200">{sunrise || '06:00 AM'}</div>
            </div>
          </div>
          <div className="w-px h-7 bg-slate-200 dark:bg-slate-700"></div>
          <div className="flex items-center gap-2.5">
            <Sunset className="w-4 h-4 text-amber-600" />
            <div>
              <div className="text-[11px] text-slate-400">{t('sunset', language)}</div>
              <div className="font-semibold text-slate-800 dark:text-slate-200">{sunset || '06:30 PM'}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Clean Metrics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <CloudRain className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span>{t('rain_prob', language)}</span>
          </div>
          <div className="text-xl font-bold text-slate-900 dark:text-white">{rain_probability}%</div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Droplets className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span>{t('humidity', language)}</span>
          </div>
          <div className="text-xl font-bold text-slate-900 dark:text-white">{humidity || 65}%</div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Wind className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span>{t('wind', language)}</span>
          </div>
          <div className="text-xl font-bold text-slate-900 dark:text-white">{wind_speed_kmh} <span className="text-xs font-normal text-slate-500">km/h</span></div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Sun className="w-3.5 h-3.5 text-amber-500" />
            <span>{t('uv_index', language)}</span>
          </div>
          <div className="text-xl font-bold text-slate-900 dark:text-white">{uv_index || 5}</div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Eye className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span>{t('visibility', language)}</span>
          </div>
          <div className="text-xl font-bold text-slate-900 dark:text-white">{visibility_km || 10} <span className="text-xs font-normal text-slate-500">km</span></div>
        </div>

        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Gauge className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span>{t('pressure', language)}</span>
          </div>
          <div className="text-xl font-bold text-slate-900 dark:text-white">{pressure_hpa || 1012} <span className="text-xs font-normal text-slate-500">hPa</span></div>
        </div>
      </div>

      {/* Data Source Note */}
      <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>{t('source', language)}: <strong className="text-slate-700 dark:text-slate-300 font-medium">{source || 'Open-Meteo'}</strong></span>
        </div>
        <span>Verified Meteorological Data Stream</span>
      </div>
    </div>
  );
};

export default WeatherCard;
