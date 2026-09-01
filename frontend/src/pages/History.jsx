import React, { useEffect, useState } from 'react';
import { useWeather } from '../context/WeatherContext';
import axios from 'axios';
import { History as HistoryIcon } from 'lucide-react';

export const History = () => {
  const { location } = useWeather();
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const resp = await axios.get(`/api/weather/historical?location=${encodeURIComponent(location)}&days=7`);
        setHistoryData(resp.data);
      } catch (e) {
        console.error("Failed to fetch history:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [location]);

  return (
    <div className="space-y-6 pb-12 text-slate-900">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <HistoryIcon className="w-6 h-6 text-sky-600" />
          Historical Weather Log — {location}
        </h2>
        <p className="text-xs text-slate-600 mt-1">Past 7 days verified weather observations and rainfall records</p>
      </div>

      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm">
        {loading ? (
          <div className="text-center py-8 text-slate-500">Loading historical log...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200 text-slate-500 uppercase font-semibold">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Max Temp (°C)</th>
                  <th className="py-3 px-4">Min Temp (°C)</th>
                  <th className="py-3 px-4">Precipitation (mm)</th>
                  <th className="py-3 px-4">Max Wind (km/h)</th>
                  <th className="py-3 px-4">Condition</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-800">
                {historyData.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 transition">
                    <td className="py-3 px-4 font-bold text-slate-900">{item.date}</td>
                    <td className="py-3 px-4">{item.max_temp_c}°C</td>
                    <td className="py-3 px-4">{item.min_temp_c}°C</td>
                    <td className="py-3 px-4">{item.precipitation_mm} mm</td>
                    <td className="py-3 px-4">{item.max_wind_kmh} km/h</td>
                    <td className="py-3 px-4">{item.condition}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
