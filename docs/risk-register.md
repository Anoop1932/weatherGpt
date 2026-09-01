# WeatherGPT Risk Register & Mitigation Matrix

| Risk ID | Identified Risk | Impact | Probability | Mitigation Strategy |
|---|---|---|---|---|
| **RISK-01** | LLM invents or hallucinates weather numbers | **CRITICAL** | Low | Grounded AI pipeline strictly validates weather evidence before LLM synthesis. |
| **RISK-02** | External weather API outage | **HIGH** | Medium | Multi-provider failover (Open-Meteo -> IMD -> Cache -> Fallback Demo Provider). |
| **RISK-03** | User misunderstands advisory as official evacuation order | **HIGH** | Low | Prominent UI warning badges stating WeatherGPT is advisory decision support only. |
| **RISK-04** | Disagreement between weather models | **MEDIUM** | High | Multi-source disagreement heuristic computes explicit confidence score (HIGH/MOD/LOW). |
