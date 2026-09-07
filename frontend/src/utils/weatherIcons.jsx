import React from 'react';
import { 
  Sun, 
  Moon, 
  CloudSun, 
  CloudMoon, 
  Cloud, 
  CloudRain, 
  CloudDrizzle, 
  CloudLightning, 
  CloudSnow, 
  CloudFog 
} from 'lucide-react';

/**
 * Single centralized weather icon mapper based strictly on WMO weather code and day/night status.
 * Never determines icon using rain probability alone.
 */
export const getWeatherIcon = (code = 0, isDay = true, className = "w-8 h-8") => {
  const numericCode = Number(code);

  // Thunderstorm
  if ([95, 96, 99].includes(numericCode)) {
    return <CloudLightning className={`${className} text-amber-500`} />;
  }

  // Snow
  if ([71, 73, 75].includes(numericCode)) {
    return <CloudSnow className={`${className} text-sky-400`} />;
  }

  // Fog
  if ([45, 48].includes(numericCode)) {
    return <CloudFog className={`${className} text-slate-400`} />;
  }

  // Rain / Rain Showers
  if ([61, 63, 65, 80, 81, 82].includes(numericCode)) {
    return <CloudRain className={`${className} text-sky-500`} />;
  }

  // Drizzle
  if ([51, 53, 55].includes(numericCode)) {
    return <CloudDrizzle className={`${className} text-sky-400`} />;
  }

  // Overcast
  if (numericCode === 3) {
    return <Cloud className={`${className} text-slate-400`} />;
  }

  // Partly Cloudy
  if ([1, 2].includes(numericCode)) {
    return isDay ? (
      <CloudSun className={`${className} text-amber-500`} />
    ) : (
      <CloudMoon className={`${className} text-sky-300`} />
    );
  }

  // Clear Sky (Code 0)
  return isDay ? (
    <Sun className={`${className} text-amber-500`} />
  ) : (
    <Moon className={`${className} text-sky-300`} />
  );
};

export const getNormalizedConditionText = (code = 0, defaultText = "Partly Cloudy") => {
  const numericCode = Number(code);
  const wmoMap = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
  };

  return wmoMap[numericCode] || defaultText;
};
