import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useWeather } from '../context/WeatherContext';
import { t, LOCALES } from '../i18n';
import { searchLocations } from '../services/locationService';
import { 
  CloudSun, 
  Search, 
  MapPin, 
  Globe, 
  Navigation, 
  Loader2, 
  History, 
  X, 
  ChevronDown,
  Menu,
  Sun,
  Moon
} from 'lucide-react';

export const Navbar = ({ onToggleMobileNav, isMobileNavOpen }) => {
  const { 
    location, 
    setLocation, 
    language, 
    setLanguage, 
    theme,
    useCurrentGeolocation, 
    geoLoading,
    recentLocs,
    removeRecentLoc
  } = useWeather();

  const [searchInput, setSearchInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showRecent, setShowRecent] = useState(false);
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  const searchContainerRef = useRef(null);
  const debounceTimer = useRef(null);

  // Debounced search logic (~300ms)
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);

    if (!searchInput || searchInput.trim().length < 2) {
      setSuggestions([]);
      setIsSearching(false);
      setShowDropdown(false);
      return;
    }

    setIsSearching(true);
    debounceTimer.current = setTimeout(async () => {
      const results = await searchLocations(searchInput);
      setSuggestions(results);
      setIsSearching(false);
      setShowDropdown(true);
      setSelectedIndex(-1);
    }, 300);

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [searchInput]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target)) {
        setShowDropdown(false);
        setShowRecent(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation
  const handleKeyDown = (e) => {
    if (!showDropdown || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
        handleSelectSuggestion(suggestions[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleSelectSuggestion = (item) => {
    setLocation(item);
    setSearchInput('');
    setShowDropdown(false);
    setShowRecent(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between gap-3 shadow-sm transition-colors">
      {/* WeatherGPT Brand Header */}
      <div className="flex items-center gap-3">
        {/* Mobile Navigation Drawer Toggle */}
        <button
          type="button"
          onClick={onToggleMobileNav}
          className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 md:hidden border border-slate-200 dark:border-slate-700 transition"
          aria-label="Toggle navigation menu"
        >
          {isMobileNavOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>

        <Link to="/" className="flex items-center gap-2.5 cursor-pointer hover:opacity-90 transition group">
          <div className="w-9 h-9 rounded-xl bg-sky-500 text-white flex items-center justify-center shadow-sm group-hover:bg-sky-600 transition shrink-0">
            <CloudSun className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-heading text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                Weather<span className="text-sky-600 dark:text-sky-400 font-normal">GPT</span>
              </h1>
            </div>
          </div>
        </Link>
      </div>

      {/* Global Location Autocomplete Search Bar */}
      <div ref={searchContainerRef} className="relative flex-1 max-w-lg mx-2">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 absolute left-3.5 text-slate-400 pointer-events-none" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onFocus={() => {
              if (suggestions.length > 0) setShowDropdown(true);
              else if (recentLocs.length > 0) setShowRecent(true);
            }}
            onKeyDown={handleKeyDown}
            placeholder={t('search_placeholder', language)}
            className="w-full bg-slate-50 dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 text-xs sm:text-sm rounded-xl pl-9 pr-24 sm:pr-28 py-2 focus:outline-none focus:border-sky-500 focus:bg-white dark:focus:bg-slate-800 transition"
          />

          {isSearching && (
            <Loader2 className="w-4 h-4 text-slate-400 animate-spin absolute right-20 sm:right-24" />
          )}

          {/* Browser Geolocation Button */}
          <button
            type="button"
            onClick={useCurrentGeolocation}
            disabled={geoLoading}
            className="absolute right-1.5 px-2 py-1 bg-white dark:bg-slate-700 hover:bg-slate-100 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-600 transition flex items-center gap-1 shrink-0 shadow-xs"
            title={t('use_my_location', language)}
          >
            <Navigation className={`w-3 h-3 text-sky-600 dark:text-sky-400 ${geoLoading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">My Location</span>
          </button>
        </div>

        {/* Autocomplete Suggestions Dropdown */}
        {showDropdown && (
          <div className="absolute left-0 right-0 top-full mt-1.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden z-50 max-h-72 overflow-y-auto">
            {isSearching ? (
              <div className="p-3 text-xs text-slate-500 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-sky-600" /> Searching location database...
              </div>
            ) : suggestions.length > 0 ? (
              suggestions.map((item, index) => (
                <div
                  key={index}
                  onClick={() => handleSelectSuggestion(item)}
                  className={`p-3 text-xs cursor-pointer flex items-start gap-2.5 transition border-b border-slate-100 dark:border-slate-700 last:border-0 ${
                    selectedIndex === index ? 'bg-sky-50 dark:bg-sky-950 text-slate-900 dark:text-white font-medium' : 'hover:bg-slate-50 dark:hover:bg-slate-700/60 text-slate-700 dark:text-slate-300'
                  }`}
                >
                  <MapPin className="w-4 h-4 text-sky-600 dark:text-sky-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="font-bold text-slate-900 dark:text-white text-sm">{item.name}</div>
                    <div className="text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
                      {[item.state, item.country].filter(Boolean).join(', ')}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 text-xs text-slate-500 dark:text-slate-400 text-center">
                {t('no_results', language)}
              </div>
            )}
          </div>
        )}

        {/* Recent Locations Dropdown */}
        {!showDropdown && showRecent && recentLocs.length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-1.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden z-50">
            <div className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <History className="w-3.5 h-3.5 text-slate-400" /> {t('recent_locations', language)}
              </span>
            </div>
            {recentLocs.map((loc, idx) => (
              <div
                key={idx}
                className="p-2.5 text-xs flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/60 transition cursor-pointer border-b border-slate-100 dark:border-slate-700 last:border-0"
              >
                <div 
                  onClick={() => { setLocation(loc); setShowRecent(false); }}
                  className="flex items-center gap-2 flex-1 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white"
                >
                  <MapPin className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
                  <span className="font-medium truncate">{loc.display_name || loc.name}</span>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeRecentLoc(loc.display_name || loc.name);
                  }}
                  className="p-1 rounded text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
                  title="Remove from recent"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right Action Bar: Theme Toggle & Language Menu */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Light / Dark Mode Toggle Button */}
        

        {/* Language Selector Dropdown */}
        <div className="relative shrink-0">
          <button
            onClick={() => setShowLangMenu(!showLangMenu)}
            className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-700 dark:text-slate-200 shadow-xs transition"
          >
            <Globe className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            <span>{LOCALES[language]?.flag} <span className="hidden sm:inline">{LOCALES[language]?.name}</span></span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showLangMenu && (
            <div className="absolute right-0 top-full mt-1.5 w-48 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden z-50 max-h-64 overflow-y-auto">
              {Object.entries(LOCALES).map(([code, info]) => (
                <button
                  key={code}
                  onClick={() => {
                    setLanguage(code);
                    setShowLangMenu(false);
                  }}
                  className={`w-full text-left px-3.5 py-2 text-xs flex items-center justify-between transition ${
                    language === code ? 'bg-sky-50 dark:bg-sky-950 text-sky-900 dark:text-sky-300 font-bold' : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                  }`}
                >
                  <span>{info.flag} {info.name}</span>
                  {info.dir === 'rtl' && <span className="text-[10px] uppercase bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 px-1.5 py-0.5 rounded">RTL</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
