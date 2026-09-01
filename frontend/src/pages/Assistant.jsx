import React from 'react';
import ChatWidget from '../components/ChatWidget';
import { Bot } from 'lucide-react';

export const Assistant = () => {
  return (
    <div className="space-y-6 pb-12 max-w-5xl mx-auto text-slate-900">
      <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            WeatherGPT Assistant
            <span className="text-xs bg-sky-50 text-sky-700 px-2.5 py-1 rounded-full border border-sky-200 font-medium">
              Verified Data Engine
            </span>
          </h2>
          <p className="text-xs text-slate-600 mt-1">
            Ask natural language questions in English, Hindi, or Punjabi. Weather queries are dynamically verified against live meteorological models.
          </p>
        </div>
        <div className="p-3 rounded-2xl bg-sky-50 text-sky-600 border border-sky-200 hidden sm:block">
          <Bot className="w-8 h-8" />
        </div>
      </div>

      <ChatWidget />
    </div>
  );
};

export default Assistant;
