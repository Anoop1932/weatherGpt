import React from 'react';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import { ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

export const RiskBadge = ({ level = 'LOW', showIcon = true, className = '' }) => {
  const { language } = useWeather();
  const normalized = (level || 'LOW').toUpperCase();

  const styles = {
    LOW: {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-700',
      icon: ShieldCheck,
      key: 'risk_low'
    },
    MODERATE: {
      bg: 'bg-amber-50 border-amber-200 text-amber-800',
      icon: AlertTriangle,
      key: 'risk_moderate'
    },
    HIGH: {
      bg: 'bg-rose-50 border-rose-200 text-rose-700',
      icon: AlertTriangle,
      key: 'risk_high'
    },
    SEVERE: {
      bg: 'bg-rose-100 border-rose-300 text-rose-800 font-bold',
      icon: AlertOctagon,
      key: 'risk_high'
    }
  };

  const current = styles[normalized] || styles.LOW;
  const Icon = current.icon;
  const label = t(current.key, language);

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${current.bg} ${className}`}>
      {showIcon && <Icon className="w-3.5 h-3.5" />}
      {label}
    </span>
  );
};

export default RiskBadge;
