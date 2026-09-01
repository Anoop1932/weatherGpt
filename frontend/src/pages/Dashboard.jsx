import React from 'react';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import WeatherCard from '../components/WeatherCard';
import WarningBanner from '../components/WarningBanner';
import ForecastChart from '../components/ForecastChart';
import WeatherMap from '../components/WeatherMap';
import ChatWidget from '../components/ChatWidget';
import RiskBadge from '../components/RiskBadge';
import { 
  Car, 
  Sprout, 
  PartyPopper, 
  CalendarDays, 
  CloudRain, 
  Sparkles,
  Sun,
  Cloud,
  CloudLightning,
  Clock,
  CheckCircle2
} from 'lucide-react';

export const Dashboard = () => {
  const { 
    forecast, 
    currentWeather, 
    language, 
    location, 
    weatherSuggestions,
    selectedForecastIndex,
    setSelectedForecastIndex
  } = useWeather();

  const dailyList = forecast?.daily || [];
  const hourlyList = forecast?.hourly?.slice(0, 12) || [];

  const skyConditionClass = currentWeather?.rain_probability > 40 ? 'sky-rain' : (currentWeather?.cloud_cover > 60 ? 'sky-cloudy' : 'sky-clear');

  const targetRainProb = dailyList[selectedForecastIndex]?.rain_probability || currentWeather?.rain_probability || 20;

  return (
    <div className={`space-y-6 pb-16 transition-colors duration-700 ${skyConditionClass}`}>
      {/* Top Warning Alert Banner */}
      <WarningBanner />

      {/* Weather-Based Smart Contextual Suggestions */}
      {weatherSuggestions.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          {weatherSuggestions.map((sug, idx) => (
            <div
              key={idx}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium bg-white border border-slate-200 text-slate-800 shadow-xs"
            >
              <span>{sug.icon}</span>
              <span>{sug.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* 1. TOP POSITION: AI Weather Assistant */}
      <div className="w-full">
        <ChatWidget />
      </div>

      {/* 2. MAIN WEATHER HERO DISPLAY */}
      <WeatherCard />

      {/* 3. 7-DAY FORECAST INTERACTIVE STRIP (Mobile Scrollable / Desktop Grid) */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-heading text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <CalendarDays className="w-5 h-5 text-sky-600" />
            <span>{t('seven_day_forecast', language)}</span>
          </h3>
          <span className="text-xs text-slate-500 font-medium">Click any day for details</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3 overflow-x-auto no-scrollbar pb-1">
          {dailyList.map((day, idx) => {
            const isSelected = selectedForecastIndex === idx;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => setSelectedForecastIndex(idx)}
                className={`bg-white border rounded-2xl p-3.5 flex flex-col justify-between space-y-2 text-xs text-left transition cursor-pointer shrink-0 shadow-xs ${
                  isSelected 
                    ? 'border-sky-500 bg-sky-50/80 shadow-md ring-2 ring-sky-400/30' 
                    : 'border-slate-200/80 hover:border-slate-300 hover:bg-slate-50'
                }`}
                aria-label={`Select forecast for ${day.day_name}, ${day.date}`}
              >
                <div className="flex items-center justify-between gap-1">
                  <span className={`font-bold text-sm ${isSelected ? 'text-sky-900' : 'text-slate-900'}`}>
                    {idx === 0 ? 'Today' : day.day_name}
                  </span>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-sky-600 shrink-0" />}
                </div>

                <div className="text-[11px] text-slate-400 font-medium">{day.date}</div>

                <div className="flex items-center gap-2 py-1">
                  <CloudRain className="w-4 h-4 text-sky-600 shrink-0" />
                  <span className="text-slate-700 text-xs font-medium truncate">{day.condition_text}</span>
                </div>

                <div className="flex items-center justify-between pt-1 border-t border-slate-100 font-semibold text-xs">
                  <span className="text-slate-500">{day.rain_probability}% rain</span>
                  <span className="text-slate-900 font-bold">{day.temp_max_c}°</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. HOURLY FORECAST HORIZONTAL TIMELINE */}
      {hourlyList.length > 0 && (
        <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 space-y-3 text-slate-900">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>{t('hourly_trend', language)}</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">Next 12 Hours</span>
          </div>

          <div className="flex items-center gap-3 overflow-x-auto no-scrollbar pt-1 pb-2">
            {hourlyList.map((hour, idx) => (
              <div
                key={idx}
                className="bg-slate-50 border border-slate-200/80 p-3 min-w-[90px] rounded-2xl flex flex-col items-center justify-between text-center space-y-1.5 shrink-0"
              >
                <span className="text-xs font-medium text-slate-600">{hour.time}</span>
                {hour.rain_probability > 40 ? (
                  <CloudRain className="w-5 h-5 text-sky-600" />
                ) : hour.weather_code === 0 ? (
                  <Sun className="w-5 h-5 text-amber-500" />
                ) : (
                  <Cloud className="w-5 h-5 text-slate-400" />
                )}
                <span className="text-base font-bold text-slate-900">{hour.temperature_c}°</span>
                <span className="text-[11px] text-slate-500">{hour.rain_probability}% rain</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. INTERACTIVE FORECAST RECHARTS GRAPH */}
      <ForecastChart />

      {/* 6. WEATHER MAP DISPLAY */}
      <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 space-y-3 text-slate-900">
        <h3 className="font-heading text-base font-bold text-slate-900">Weather Map & Radar</h3>
        <div className="h-72 w-full rounded-2xl overflow-hidden border border-slate-200">
          <WeatherMap />
        </div>
      </div>

      {/* 7. DECISION SUPPORT ADVISORIES (100% Localized Title + Descriptions) */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-sky-600" />
          <h3 className="font-heading text-lg font-bold text-slate-900 tracking-tight">
            {t('decision_support', language)}
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Travel Advisory */}
          <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-700">
                <Car className="w-4 h-4" />
              </div>
              <RiskBadge level={targetRainProb > 50 ? 'MODERATE' : 'LOW'} />
            </div>
            <h4 className="font-heading text-sm font-bold text-slate-900">{t('travel_advisory', language)}</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              {targetRainProb > 50
                ? t('travel_caution', language).replace('{location}', location).replace('{prob}', targetRainProb)
                : t('travel_good', language).replace('{location}', location)}
            </p>
          </div>

          {/* Agricultural Spraying */}
          <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-700">
                <Sprout className="w-4 h-4" />
              </div>
              <RiskBadge level={targetRainProb > 50 ? 'HIGH' : 'LOW'} />
            </div>
            <h4 className="font-heading text-sm font-bold text-slate-900">{t('agri_advisory', language)}</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              {targetRainProb > 50
                ? t('agri_caution', language).replace('{location}', location).replace('{prob}', targetRainProb)
                : t('agri_good', language).replace('{location}', location)}
            </p>
          </div>

          {/* Outdoor Events */}
          <div className="bg-white border border-slate-200/80 shadow-sm rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-xl bg-slate-50 border border-slate-200 text-slate-700">
                <PartyPopper className="w-4 h-4" />
              </div>
              <RiskBadge level={targetRainProb > 50 ? 'MODERATE' : 'LOW'} />
            </div>
            <h4 className="font-heading text-sm font-bold text-slate-900">{t('event_advisory', language)}</h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              {targetRainProb > 50
                ? t('event_caution', language).replace('{location}', location).replace('{prob}', targetRainProb)
                : t('event_good', language).replace('{location}', location)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
