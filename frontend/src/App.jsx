import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { WeatherProvider } from './context/WeatherContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Assistant from './pages/Assistant';
import Forecast from './pages/Forecast';
import Alerts from './pages/Alerts';
import MapPage from './pages/MapPage';

export function App() {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

  return (
    <WeatherProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-[#f0f6ff] text-slate-900 font-['Inter',sans-serif] overflow-x-hidden">
          {/* Top Header with Autocomplete Location Search */}
          <Navbar 
            onToggleMobileNav={() => setIsMobileNavOpen(!isMobileNavOpen)} 
            isMobileNavOpen={isMobileNavOpen}
          />

          <div className="flex flex-1 relative">
            {/* Navigation Sidebar & Mobile Drawer Overlay */}
            <Sidebar 
              isMobileOpen={isMobileNavOpen} 
              onCloseMobile={() => setIsMobileNavOpen(false)} 
            />

            {/* Main Application Area (Responsive max-w-7xl centered container) */}
            <main className="flex-1 p-3 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-x-hidden">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/forecast" element={<Forecast />} />
                <Route path="/map" element={<MapPage />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/assistant" element={<Assistant />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </WeatherProvider>
  );
}

export default App;
