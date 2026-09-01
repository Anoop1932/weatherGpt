export const generateWeatherSuggestions = (currentWeather, warnings = []) => {
  if (!currentWeather) return [];

  const suggestions = [];

  const rainProb = currentWeather.rain_probability || 0;
  const tempC = currentWeather.temperature_c || 25;
  const windKmh = currentWeather.wind_speed_kmh || 10;
  const visKm = currentWeather.visibility_km || 10;
  const uvIndex = currentWeather.uv_index || 4;

  if (warnings && warnings.length > 0) {
    suggestions.push({
      type: 'warning',
      icon: '⚠️',
      text: 'Severe weather warning is active for this region.',
      badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30'
    });
  }

  if (rainProb >= 50) {
    suggestions.push({
      type: 'rain',
      icon: '☔',
      text: `Carry an umbrella today (${rainProb}% rain chance).`,
      badgeClass: 'bg-sky-500/10 text-sky-400 border-sky-500/30'
    });
  }

  if (windKmh >= 25) {
    suggestions.push({
      type: 'wind',
      icon: '💨',
      text: `Strong winds expected (${windKmh} km/h).`,
      badgeClass: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
    });
  }

  if (tempC >= 35) {
    suggestions.push({
      type: 'heat',
      icon: '🌡️',
      text: `High temperatures expected (${tempC}°C). Stay hydrated.`,
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    });
  }

  if (uvIndex >= 6) {
    suggestions.push({
      type: 'uv',
      icon: '☀️',
      text: `UV index is high (${uvIndex}). Sun protection advised.`,
      badgeClass: 'bg-amber-500/10 text-amber-400 border-amber-500/30'
    });
  }

  if (visKm <= 3.0) {
    suggestions.push({
      type: 'fog',
      icon: '🌫️',
      text: `Low visibility (${visKm} km) may affect travel safety.`,
      badgeClass: 'bg-purple-500/10 text-purple-400 border-purple-500/30'
    });
  }

  if (suggestions.length === 0) {
    suggestions.push({
      type: 'pleasant',
      icon: '🌤️',
      text: 'Good conditions for outdoor activities and travel.',
      badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
    });
  }

  return suggestions;
};

export const generateDynamicContextualQuestions = (locationName, currentWeather) => {
  const loc = locationName || 'Current Location';
  const rainProb = currentWeather?.rain_probability || 0;

  if (rainProb > 40) {
    return [
      `Will it rain tonight in ${loc}?`,
      `Is tomorrow morning good for travel in ${loc}?`,
      `Should I carry an umbrella today in ${loc}?`,
      `How will the weather change this week in ${loc}?`
    ];
  }

  return [
    `Will it rain tomorrow in ${loc}?`,
    `Is tomorrow good for outdoor events in ${loc}?`,
    `Is farming spraying suitable tomorrow in ${loc}?`,
    `How will temperature change this week in ${loc}?`
  ];
};
