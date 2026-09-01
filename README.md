# WeatherGPT — Conversational Weather Intelligence & Decision Support
### Smart India Hackathon 2026 — Problem Statement SIH26068

WeatherGPT is an enterprise-grade Conversational Weather Intelligence & Decision Support Platform engineered around the fundamental operational pipeline:

$$\mathbf{WEATHER} \longrightarrow \mathbf{RISK} \longrightarrow \mathbf{DECISION} \longrightarrow \mathbf{ACTION}$$

Unlike generic chatbots or static weather dashboards, WeatherGPT operates as a grounded intelligence layer above validated meteorological data sources (Open-Meteo, IMD, MAUSAM), guaranteeing zero LLM hallucination of weather facts through strict evidence extraction, rule-based risk calculation, and actionable decision synthesis.

---

## Key Features

- **Zero Hallucination Grounded AI**: The LLM never invents weather metrics. Weather facts (temperature, rain probability, wind speed, warnings) are fetched deterministically from APIs and injected into grounded prompt templates.
- **Multi-Lingual Query Parser**: Supports natural queries in English, Hindi, and Hinglish (e.g., *"Kal Amritsar mein baarish hogi?"*, *"Kal travel karna safe hai?"*, *"Kal spraying karna suitable hai?"*).
- **Deterministic Risk Engine**: Separate rule modules evaluate rain, wind, visibility, and official weather warnings into clear risk levels (**LOW**, **MODERATE**, **HIGH**, **SEVERE**).
- **Multi-Source Disagreement Resolver**: Evaluates forecast confidence (**HIGH**, **MODERATE**, **LOW**) when independent weather models show variance.
- **Voice Intelligence**: Browser Web Speech API integration (Speech-To-Text and Text-To-Speech) in English and Hindi.
- **Interactive Weather Maps & Trend Graphs**: Leaflet map integration with station markers and Recharts 24-hour temperature & rain probability trend charts.
- **Official Warning Bulletins**: Prominently displays severe alerts from official meteorological authorities (IMD/MAUSAM).
- **Resilient Fallback Mode**: Automatic multi-tier failover (Live API -> Cache -> Official Bulletin -> Fallback Demo Engine).

---

## Tech Stack

- **Frontend**: React 18, Vite, Tailwind CSS, React Router, Recharts, Leaflet, Lucide React, Axios.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, HTTPX, SQLAlchemy (Async).
- **Database & Cache**: SQLite / PostgreSQL (PostGIS ready), Redis (with in-memory dictionary fallback).
- **AI Engine**: Gemini API (`google-genai`) with Grounded Fallback Synthesizer.

---

## Project Structure

```
weaathergpt/
├── frontend/                  # React + Vite + Tailwind CSS Frontend
│   ├── src/
│   │   ├── components/        # Navbar, WeatherCard, ForecastChart, WarningBanner, WeatherMap, ChatWidget
│   │   ├── pages/             # Dashboard, Assistant, Forecast, Alerts, MapPage, History, Settings, About
│   │   ├── i18n/              # English & Hindi translation files (en.json, hi.json)
│   │   ├── context/           # WeatherContext state manager
│   │   └── services/          # Web Speech API voice wrapper
│   ├── package.json
│   └── vite.config.js
│
├── backend/                   # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint & router mounts
│   │   ├── config.py          # Environment settings
│   │   ├── database.py        # SQLAlchemy async database setup
│   │   ├── api/               # REST API endpoints (health, weather, chat, voice)
│   │   ├── weather/           # OpenMeteo, IMD, Fallback, and WeatherOrchestrator
│   │   ├── risk/              # Deterministic risk engine (rain, wind, visibility, warnings)
│   │   ├── ai/                # Multi-lingual NLP parser & Grounded LLM engine
│   │   └── cache/             # Redis client with in-memory fallback
│   ├── tests/                 # Pytest automated test suite
│   ├── requirements.txt
│   └── .env.example
│
├── docs/                      # Technical Documentation Suite
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   ├── testing.md
│   ├── security.md
│   └── risk-register.md
│
├── docker-compose.yml
└── README.md
```

---

## Quick Start Guide

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate  # Windows

# Install backend dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend Web Dashboard will be available at: `http://localhost:5173`

---

## Environment Variables Configuration

Copy `backend/.env.example` to `backend/.env`:

```env
ENVIRONMENT=development
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]

DATABASE_URL=sqlite+aiosqlite:///./weathergpt.db
REDIS_URL=redis://localhost:6379/0

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

DEMO_MODE=false
DEFAULT_LOCATION=Amritsar
```

---

## Running Automated Tests

```bash
cd backend
pytest -v
```

---

## API Summary

- `GET /api/health` — System status & engine diagnostics
- `GET /api/weather/current?location=Amritsar` — Verified current weather
- `GET /api/weather/forecast?location=Amritsar&days=7` — 7-day forecast data
- `GET /api/weather/warnings?location=Amritsar` — Active official severe warnings
- `POST /api/weather/query` — Natural language query & decision advisory
- `POST /api/voice/query` — Voice query transcript processing

---

## Official Disclaimer

WeatherGPT acts strictly as a conversational intelligence layer above trusted meteorological data sources. WeatherGPT outputs advisory decision support and does NOT replace official emergency authorities (IMD, MAUSAM, NDMA, State Disaster Management Authorities) nor issue legally binding evacuation orders.
