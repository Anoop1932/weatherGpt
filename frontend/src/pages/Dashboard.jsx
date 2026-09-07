import React, { useEffect, useRef } from 'react';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import WeatherCard from '../components/WeatherCard';
import WarningBanner from '../components/WarningBanner';
import ForecastChart from '../components/ForecastChart';
import WeatherMap from '../components/WeatherMap';
import ChatWidget from '../components/ChatWidget';
import RiskBadge from '../components/RiskBadge';
import { getWeatherIcon } from '../utils/weatherIcons';
import { gsap } from 'gsap';
import { 
  Car, 
  Sprout, 
  PartyPopper, 
  CalendarDays, 
  Sparkles,
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

  const containerRef = useRef(null);

  useEffect(() => {
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return;
    }
    if (containerRef.current) {
      gsap.fromTo(
        containerRef.current.querySelectorAll('.gsap-fade-in'),
        { opacity: 0, y: 12 },
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.06, ease: 'power2.out' }
      );
    }
  }, [location]);

  const dailyList = forecast?.daily || [];
  const hourlyList = forecast?.hourly?.slice(0, 12) || [];

  const targetRainProb = dailyList[selectedForecastIndex]?.rain_probability || currentWeather?.rain_probability || 20;

  return (
    <div ref={containerRef} className="space-y-6 pb-16 transition-colors duration-700">
      {/* Top Warning Alert Banner */}
      <WarningBanner />

      {/* Weather-Based Smart Contextual Suggestions */}
      {weatherSuggestions.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 gsap-fade-in">
          {weatherSuggestions.map((sug, idx) => (
            <div
              key={idx}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 shadow-xs"
            >
              <span>{sug.icon}</span>
              <span>{sug.text}</span>
            </div>
          ))}
        </div>
      )}

      {/* 1. TOP POSITION: AI Weather Assistant */}
      <div className="w-full gsap-fade-in">
        <ChatWidget />
      </div>

      {/* 2. MAIN WEATHER HERO DISPLAY */}
      <div className="gsap-fade-in">
        <WeatherCard />
      </div>

      {/* 3. 7-DAY FORECAST INTERACTIVE STRIP */}
      <div className="space-y-3 gsap-fade-in">
        <div className="flex items-center justify-between">
          <h3 className="font-heading text-lg font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
            <CalendarDays className="w-5 h-5 text-sky-600 dark:text-sky-400" />
            <span>{t('seven_day_forecast', language)}</span>
          </h3>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">Click any day for details</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3 overflow-x-auto no-scrollbar pb-1">
          {dailyList.map((day, idx) => {
            const isSelected = selectedForecastIndex === idx;
            return (
              <button
                key={idx}
                type="button"
                onClick={() => setSelectedForecastIndex(idx)}
                className={`bg-white dark:bg-slate-800/90 border rounded-2xl p-3.5 flex flex-col justify-between space-y-2 text-xs text-left transition cursor-pointer shrink-0 shadow-xs ${
                  isSelected 
                    ? 'border-sky-500 dark:border-sky-400 bg-sky-50/80 dark:bg-sky-950/40 shadow-md ring-2 ring-sky-400/30' 
                    : 'border-slate-200/80 dark:border-slate-700/80 hover:border-slate-300 dark:hover:border-slate-600 hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
                aria-label={`Select forecast for ${day.day_name}, ${day.date}`}
              >
                <div className="flex items-center justify-between gap-1">
                  <span className={`font-bold text-sm ${isSelected ? 'text-sky-900 dark:text-sky-300' : 'text-slate-900 dark:text-white'}`}>
                    {idx === 0 ? 'Today' : day.day_name}
                  </span>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-sky-600 dark:text-sky-400 shrink-0" />}
                </div>

                <div className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">{day.date}</div>

                <div className="flex items-center gap-2 py-1">
                  <div className="shrink-0">
                    {getWeatherIcon(day.weather_code, true, "w-5 h-5")}
                  </div>
                  <span className="text-slate-700 dark:text-slate-300 text-xs font-medium truncate">{day.condition_text}</span>
                </div>

                <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-700/80 font-semibold text-xs">
                  <span className="text-slate-500 dark:text-slate-400">{day.rain_probability}% rain</span>
                  <span className="text-slate-900 dark:text-white font-bold">{day.temp_max_c}°</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. HOURLY FORECAST HORIZONTAL TIMELINE */}
      {hourlyList.length > 0 && (
        <div className="bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/80 shadow-sm rounded-3xl p-5 space-y-3 text-slate-900 dark:text-slate-100 gsap-fade-in">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 pb-2">
            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200 flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <span>{t('hourly_trend', language)}</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">Next 12 Hours</span>
          </div>

          <div className="flex items-center gap-3 overflow-x-auto no-scrollbar pt-1 pb-2">
            {hourlyList.map((hour, idx) => {
              const hourNum = parseInt(hour.time.split(':')[0], 10) || 12;
              const isDay = hourNum >= 6 && hourNum < 19;
              return (
                <div
                  key={idx}
                  className="bg-slate-50 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700 p-3 min-w-[90px] rounded-2xl flex flex-col items-center justify-between text-center space-y-1.5 shrink-0"
                >
                  <span className="text-xs font-medium text-slate-600 dark:text-slate-400">{hour.time}</span>
                  <div className="shrink-0">
                    {getWeatherIcon(hour.weather_code, isDay, "w-5 h-5")}
                  </div>
                  <span className="text-base font-bold text-slate-900 dark:text-white">{hour.temperature_c}°</span>
                  <span className="text-[11px] text-slate-500 dark:text-slate-400">{hour.rain_probability}% rain</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 5. INTERACTIVE FORECAST RECHARTS GRAPH */}
      <div className="gsap-fade-in">
        <ForecastChart />
      </div>

      {/* 6. WEATHER MAP DISPLAY */}
      <div className="bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/80 shadow-sm rounded-3xl p-5 space-y-3 text-slate-900 dark:text-slate-100 gsap-fade-in">
        <h3 className="font-heading text-base font-bold text-slate-900 dark:text-white">Weather Map & Radar</h3>
        <div className="h-72 w-full rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700">
          <WeatherMap />
        </div>
      </div>

      {/* 7. DECISION SUPPORT ADVISORIES */}
      <div className="space-y-3 gsap-fade-in">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-sky-600 dark:text-sky-400" />
          <h3 className="font-heading text-lg font-bold text-slate-900 dark:text-white tracking-tight">
            {t('decision_support', language)}
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Travel Advisory */}
          <div className="bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/80 shadow-sm rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
                <Car className="w-4 h-4" />
              </div>
              <RiskBadge level={targetRainProb > 50 ? 'MODERATE' : 'LOW'} />
            </div>
            <h4 className="font-heading text-sm font-bold text-slate-900 dark:text-white">{t('travel_advisory', language)}</h4>
            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {targetRainProb > 50
                ? t('travel_caution', language).replace('{location}', location).replace('{prob}', targetRainProb)
                : t('travel_good', language).replace('{location}', location)}
            </p>
          </div>

          {/* Agricultural Spraying */}
          <div className="bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/80 shadow-sm rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
                <Sprout className="w-4 h-4" />
              </div>
              <RiskBadge level={targetRainProb > 50 ? 'HIGH' : 'LOW'} />
            </div>
            <h4 className="font-heading text-sm font-bold text-slate-900 dark:text-white">{t('agri_advisory', language)}</h4>
            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
              {targetRainProb > 50
                ? t('agri_caution', language).replace('{location}', location).replace('{prob}', targetRainProb)
                : t('agri_good', language).replace('{location}', location)}
            </p>
          </div>

          {/* Outdoor Events */}
          <div className="bg-white dark:bg-slate-800/90 border border-slate-200/80 dark:border-slate-700/80 shadow-sm rounded-3xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
                <PartyPopper className="w-4 h-4" />
              </div>
              <RiskBadge level={targetRainProb > 50 ? 'MODERATE' : 'LOW'} />
            </div>
            <h4 className="font-heading text-sm font-bold text-slate-900 dark:text-white">{t('event_advisory', language)}</h4>
            <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
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
