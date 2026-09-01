import React from 'react';
import { useWeather } from '../context/WeatherContext';
import { RiskBadge } from './RiskBadge';
import { AlertOctagon, CheckCircle2 } from 'lucide-react';

export const WarningBanner = () => {
  const { warnings, location } = useWeather();

  // If no verified warnings exist, render a clean, subtle status bar
  if (!warnings || warnings.length === 0) {
    return (
      <div className="bg-emerald-50/80 border border-emerald-200 rounded-2xl p-3 flex items-center justify-between text-xs text-emerald-900 shadow-xs">
        <div className="flex items-center gap-2 font-medium">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>No active official weather warnings for <strong className="font-bold">{location}</strong></span>
        </div>
        <span className="text-[11px] text-emerald-700 font-medium hidden sm:inline">Source: Meteorological Watch</span>
      </div>
    );
  }

  // Render official verified warnings only when actual alert data is present
  return (
    <div className="space-y-3">
      {warnings.map((warn, idx) => (
        <div
          key={warn.id || idx}
          className="bg-amber-50 border border-amber-200 rounded-2xl p-4 space-y-2 text-amber-900 shadow-xs"
        >
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-xl bg-amber-100 text-amber-700 shrink-0 mt-0.5">
                <AlertOctagon className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs uppercase font-bold text-amber-700 tracking-wider">
                    {warn.warning_type || 'OFFICIAL WARNING'}
                  </span>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-white text-amber-800 border border-amber-200 font-medium">
                    {warn.source || 'Verified Source'}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-amber-950 mt-1">{warn.headline}</h4>
                <p className="text-xs text-amber-800 mt-1 leading-relaxed">
                  {warn.description}
                </p>
                <div className="flex flex-wrap items-center gap-4 text-[11px] text-amber-700 mt-2">
                  {warn.affected_area && <span>Affected: <strong className="text-amber-900">{warn.affected_area}</strong></span>}
                  {warn.issued_at && <span>Issued: <strong className="text-amber-900">{warn.issued_at}</strong></span>}
                  {warn.valid_until && <span>Valid Until: <strong className="text-amber-900">{warn.valid_until}</strong></span>}
                </div>
              </div>
            </div>

            <RiskBadge level={warn.severity || 'MODERATE'} />
          </div>
        </div>
      ))}
    </div>
  );
};

export default WarningBanner;
