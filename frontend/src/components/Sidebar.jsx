import React from 'react';
import { NavLink } from 'react-router-dom';
import { useWeather } from '../context/WeatherContext';
import { t } from '../i18n';
import { 
  CloudSun, 
  Bot, 
  CalendarDays, 
  ShieldAlert, 
  MapPin,
  X
} from 'lucide-react';

export const Sidebar = ({ isMobileOpen, onCloseMobile }) => {
  const { language } = useWeather();

  const navItems = [
    { path: '/', label: t('dashboard', language), icon: CloudSun },
    { path: '/forecast', label: t('forecast', language), icon: CalendarDays },
    { path: '/map', label: t('map', language), icon: MapPin },
    { path: '/alerts', label: t('alerts', language), icon: ShieldAlert },
    { path: '/assistant', label: t('ai_assistant', language), icon: Bot },
  ];

  return (
    <>
      {/* Desktop Sidebar (Fixed Left) */}
      <aside className="w-56 bg-white/80 backdrop-blur-md border-r border-slate-200/80 hidden md:flex flex-col justify-between py-6 px-3 shrink-0 min-h-[calc(100vh-65px)] shadow-xs">
        <div className="space-y-1">
          <div className="px-3 pb-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Navigation
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition ${
                    isActive
                      ? 'bg-sky-50 text-sky-700 font-bold border border-sky-200 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0 text-sky-600" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>

        <div className="pt-4 border-t border-slate-200/80 px-3 text-xs text-slate-500">
          <div className="font-bold text-slate-800 font-heading">WeatherGPT Intelligence</div>
          <div className="text-[11px] text-slate-400 mt-0.5">SIH26068 Meteorological Stream</div>
        </div>
      </aside>

      {/* Mobile Navigation Drawer Overlay */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          {/* Backdrop Blur */}
          <div 
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={onCloseMobile}
          />

          {/* Slide-out Drawer Panel */}
          <div className="relative w-64 max-w-[80vw] bg-white border-r border-slate-200 p-5 flex flex-col justify-between z-50 shadow-2xl">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="font-heading font-bold text-slate-900 text-base">Navigation</div>
                <button
                  type="button"
                  onClick={onCloseMobile}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <nav className="space-y-1.5">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      onClick={onCloseMobile}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-medium transition ${
                          isActive
                            ? 'bg-sky-50 text-sky-900 font-bold border border-sky-200'
                            : 'text-slate-700 hover:text-slate-900 hover:bg-slate-50'
                        }`
                      }
                    >
                      <Icon className="w-4 h-4 shrink-0 text-sky-600" />
                      <span>{item.label}</span>
                    </NavLink>
                  );
                })}
              </nav>
            </div>

            <div className="pt-4 border-t border-slate-100 text-xs text-slate-500">
              <div className="font-bold text-slate-800 font-heading">WeatherGPT Intelligence</div>
              <div className="text-[11px] text-slate-400 mt-0.5">SIH26068 Mobile Edition</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;
