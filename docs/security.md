# WeatherGPT Security Architecture & Protocols

## Security Highlights

1. **Environment Key Separation**:
   - API keys (e.g. `GEMINI_API_KEY`, `SECRET_KEY`) are managed strictly on the backend server via `.env`.
   - Zero credentials or secrets are exposed in the frontend client codebase.

2. **CORS Enforcement**:
   - Explicit CORS origin allowlist configuration (`CORS_ORIGINS`) preventing unauthorized cross-origin requests.

3. **Prompt Injection Defense**:
   - User queries are never executed directly as LLM instructions.
   - The NLP parser sanitizes user input and isolates intent and entities.
   - Grounded weather facts and risk engine evaluations are passed into system instructions as immutable context.

4. **Public Authority Protection**:
   - WeatherGPT outputs advisory decision support and explicitly disclaims emergency evacuation authority.
