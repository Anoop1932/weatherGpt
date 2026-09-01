# WeatherGPT System Architecture

## Architecture Overview

WeatherGPT is designed as a conversational weather intelligence and decision support platform adhering to the pipeline:

$$\text{WEATHER} \longrightarrow \text{RISK} \longrightarrow \text{DECISION} \longrightarrow \text{ACTION}$$

```
                           +------------------------+
                           |  User Interface (Web)  |
                           |  React + Vite + Tail   |
                           +-----------+------------+
                                       |
                                       | Natural Language / Voice
                                       v
                           +------------------------+
                           | FastAPI Backend Router |
                           +-----------+------------+
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        v                              v                              v
+---------------+             +-----------------+           +-------------------+
|  NLP Parser   |             | Weather Provider|           | Deterministic Risk|
| (EN/HI/Intent)|             |  Orchestrator   |           |      Engine       |
+-------+-------+             +--------+--------+           +---------+---------+
        |                              |                              |
        | Entity Extracted             | Validated Weather Facts      | Safety Profile
        +------------------------------+------------------------------+
                                       |
                                       v
                         +----------------------------+
                         |  Grounded LLM Synthesizer  |
                         |  (Gemini API / Fallback)   |
                         +-------------+--------------+
                                       |
                                       v
                         +----------------------------+
                         |  Actionable Decision UI    |
                         +----------------------------+
```

---

## Core Principles

1. **Zero Hallucinated Facts**: Weather facts (temperatures, precipitation probabilities, wind speeds, pressure, visibility, warnings) are fetched from validated meteorological providers and supplied to the LLM as immutable ground truth.
2. **Isolated Risk Calculation**: Risk thresholds for rain, wind, visibility, and official advisories are evaluated deterministically by dedicated Python rules engines, preventing the LLM from hallucinating safety thresholds.
3. **Multi-Source Confidence Scoring**: When model outputs vary across weather services (Open-Meteo vs IMD), a source disagreement heuristic computes a confidence score (**HIGH**, **MODERATE**, **LOW**).
4. **Resilient Contingency Execution**: Live APIs automatically fallback to cached LKG (Last-Known-Good) observations and controlled demo data feeds.
