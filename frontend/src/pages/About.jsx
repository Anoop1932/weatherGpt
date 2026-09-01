import React from 'react';
import { CloudLightning, CheckCircle2 } from 'lucide-react';

export const About = () => {
  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto text-slate-900">
      <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-2xl bg-sky-500 text-white shadow-sm">
            <CloudLightning className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">WeatherGPT</h2>
            <p className="text-xs text-sky-700 font-semibold">Smart India Hackathon 2026 — SIH26068</p>
          </div>
        </div>

        <p className="text-sm text-slate-600 leading-relaxed">
          WeatherGPT is an intelligent weather application and decision support platform built on the core principle:
        </p>

        <div className="p-4 rounded-2xl bg-sky-50 border border-sky-200 text-center font-bold text-sky-900 tracking-wider text-sm sm:text-base">
          WEATHER → RISK → DECISION → ACTION
        </div>

        <h3 className="text-base font-bold text-slate-900 pt-2">Core Grounding & Architecture Principles</h3>
        <ul className="space-y-2 text-xs text-slate-600">
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span><strong className="text-slate-900">Zero Hallucinated Numbers:</strong> Weather facts are verified deterministically from live meteorological data.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span><strong className="text-slate-900">Deterministic Risk Engine:</strong> Safety thresholds for rain, wind, visibility, and warnings are computed by rule modules.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span><strong className="text-slate-900">Multilingual Decision Support:</strong> Natural language queries in English, Hindi, and Punjabi for travel, agriculture, and outdoor events.</span>
          </li>
          <li className="flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <span><strong className="text-slate-900">Official Authorities Layer:</strong> Operates as an advisory layer above IMD, MAUSAM, and Open-Meteo services.</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default About;
