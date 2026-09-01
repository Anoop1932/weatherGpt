# WeatherGPT API Reference

All REST API endpoints are hosted under `/api`. Interactive OpenAPI documentation is accessible at `/docs`.

---

## 1. Health Endpoint

### `GET /api/health`
Returns service status, environment details, Redis connectivity, and active LLM engine provider.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "WeatherGPT Intelligence Platform API",
  "version": "1.0.0-SIH26068",
  "timestamp": "2026-08-26T10:15:00.000Z",
  "environment": "development",
  "demo_mode": false,
  "redis_connected": true,
  "llm_provider": "Gemini Grounded Engine"
}
```

---

## 2. Weather Endpoints

### `GET /api/weather/current`
Fetches current weather observations for a target location or lat/lon coordinates.

**Parameters:**
- `location` (string, optional, default: "Amritsar")
- `lat` (float, optional)
- `lon` (float, optional)

---

### `GET /api/weather/forecast`
Fetches 7-day hourly and daily weather forecast data.

**Parameters:**
- `location` (string, optional)
- `days` (int, default: 7)

---

### `GET /api/weather/warnings`
Fetches official severe weather alerts and bulletins.

---

## 3. Grounded Conversational AI Endpoints

### `POST /api/weather/query`
Executes natural language query parsing, weather evidence retrieval, risk engine evaluation, and grounded answer synthesis.

**Request Payload:**
```json
{
  "query": "Kal Amritsar mein baarish hogi?",
  "location": "Amritsar",
  "language": "auto"
}
```

**Response:**
```json
{
  "raw_query": "Kal Amritsar mein baarish hogi?",
  "detected_language": "hi",
  "extracted_intent": "forecast",
  "resolved_location": "Amritsar",
  "resolved_date": "2026-08-27",
  "weather_facts": {
    "temperature_c": 31.0,
    "rain_probability": 65.0,
    "precipitation_mm": 12.5,
    "condition_text": "Moderate Rain"
  },
  "risk_evaluation": {
    "risk_level": "HIGH",
    "category": "forecast",
    "reasons": ["High rain probability (65%) with estimated precipitation of 12.5mm."],
    "recommendation": "High likelihood of rain. Carry rain protection.",
    "confidence": "HIGH"
  },
  "grounded_answer": "Kal Amritsar mein baarish ki probability approximately 65% hai...",
  "source": "Open-Meteo Meteorological Service",
  "confidence": "HIGH"
}
```
