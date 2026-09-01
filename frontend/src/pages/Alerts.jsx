import React from 'react';
import WarningBanner from '../components/WarningBanner';
import { ShieldAlert, Info } from 'lucide-react';

export const Alerts = () => {
  return (
    <div className="space-y-6 pb-12 text-slate-900">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <ShieldAlert className="w-6 h-6 text-rose-600" />
          Severe Weather Alerts & Official Bulletins
        </h2>
        <p className="text-xs text-slate-600 mt-1">
          Real-time weather watch notices aggregated from IMD, MAUSAM, and meteorological centers.
        </p>
      </div>

      <WarningBanner />

      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-3">
        <h3 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Info className="w-4 h-4 text-sky-600" />
          Official Emergency Disclaimer
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          WeatherGPT serves as an intelligent advisory layer above trusted meteorological data sources. WeatherGPT does NOT replace official authorities (IMD, MAUSAM, NDMA, State Disaster Authorities). WeatherGPT outputs decision support advisories and does NOT issue binding evacuation orders.
        </p>
      </div>
    </div>
  );
};

export default Alerts;
