from typing import Dict, Any, Tuple, List


def evaluate_rain_risk(
    rain_probability: float,
    precipitation_mm: float = 0.0,
    context: str = "general"
) -> Tuple[str, List[str], str]:
    """
    Evaluates rain risk level, reasons, and recommendations deterministically based on thresholds:
    - probability < 30% -> LOW
    - 30% - 60% -> MODERATE
    - > 60% -> HIGH
    """
    reasons = []

    if rain_probability < 30.0:
        level = "LOW"
        reasons.append(f"Low rain probability ({rain_probability}%). Precipitation expected to be minimal ({precipitation_mm}mm).")
        rec = "Weather conditions for rain are favorable. No rain gear strictly required."
    elif 30.0 <= rain_probability <= 60.0:
        level = "MODERATE"
        reasons.append(f"Moderate rain probability ({rain_probability}%). Chance of scattered rain/showers.")
        rec = "Carry an umbrella or light raincoat. Keep track of short-term weather updates."
    else:
        level = "HIGH"
        reasons.append(f"High rain probability ({rain_probability}%) with estimated precipitation of {precipitation_mm}mm.")
        rec = "High likelihood of rain. Carry rain protection, secure outdoor gear, and expect localized waterlogging."

    # Contextual tweaks
    if context == "agriculture":
        if level in ["MODERATE", "HIGH"]:
            rec = "Unsuitable for pesticide or fertilizer spraying. High precipitation risk leads to chemical wash-off."
        else:
            rec = "Favorable for pesticide/fertilizer spraying provided wind speeds remain calm."
    elif context == "travel":
        if level == "HIGH":
            rec = "Exercise caution during travel. Allow extra travel time for wet roads and reduced traction."
    elif context == "event":
        if level in ["MODERATE", "HIGH"]:
            rec = "Outdoor event disruption risk is elevated. Consider setting up waterproof canopies or indoor backup options."

    return level, reasons, rec
