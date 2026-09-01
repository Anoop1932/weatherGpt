# WeatherGPT Database Schema Documentation

WeatherGPT supports both PostgreSQL (with PostGIS extensions for spatial queries) and SQLite (with JSON column extensions for dev/testing).

---

## Entity Relationship Summary

```
   +---------------+          +--------------------+
   |     User      |          |    Location        |
   +---------------+          +--------------------+
   | id            |          | id                 |
   | email         |          | name               |
   | language_pref |          | latitude, longitude|
   +---------------+          +--------------------+
                                        |
           +----------------------------+----------------------------+
           |                            |                            |
           v                            v                            v
+----------------------+    +-----------------------+    +------------------------+
| WeatherObservation   |    |       Forecast        |    |        Warning         |
+----------------------+    +-----------------------+    +------------------------+
| id, location_name    |    | id, location_name     |    | id, location_name      |
| temperature_c        |    | forecast_date         |    | warning_type, severity |
| rain_probability     |    | data_json (hourly)    |    | issued_at, valid_until |
| observed_at, source  |    | confidence, source    |    | source                 |
+----------------------+    +-----------------------+    +------------------------+
```

---

## Tables Overview

1. **users**: User preferences, default location, language choice (`en`/`hi`).
2. **locations**: Normalized geographical entities with precise `latitude` and `longitude`.
3. **weather_observations**: Real-time station surface observations.
4. **forecasts**: Stored hourly and daily forecasts with confidence metrics.
5. **warnings**: Active official meteorological watch notices and severe weather alerts.
6. **weather_queries**: Log of natural language user queries, extracted entities, risk evaluation, and synthesized answers.
7. **recommendations**: Domain decision support advice (Travel, Agriculture, Events).
8. **historical_weather**: Archived weather observations for historical trend analytics.
