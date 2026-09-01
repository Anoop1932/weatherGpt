from typing import List, Tuple, Dict, Any


def evaluate_warning_risk(
    warnings: List[Dict[str, Any]],
    context: str = "general"
) -> Tuple[str, List[str], str]:
    """
    Evaluates official weather warnings:
    - Any SEVERE warning -> SEVERE
    - Any HIGH warning -> HIGH
    - Any MODERATE warning -> MODERATE
    - None -> LOW
    """
    if not warnings:
        return "LOW", [], "No active official severe weather warnings for this location."

    severities = [w.get("severity", "LOW").upper() for w in warnings]
    reasons = [f"Official Alert: {w.get('headline')} ({w.get('source')})" for w in warnings]

    if "SEVERE" in severities:
        level = "SEVERE"
        rec = "ACTIVE SEVERE WEATHER WARNING. Monitor official emergency authorities (IMD/NDMA/State Disaster Authority) and follow safety guidelines."
    elif "HIGH" in severities:
        level = "HIGH"
        rec = "High priority weather warning active. Restrict non-essential travel and stay updated."
    elif "MODERATE" in severities:
        level = "MODERATE"
        rec = "Moderate weather alert active. Take precautionary steps for outdoor activities."
    else:
        level = "LOW"
        rec = "Low severity advisory."

    return level, reasons, rec
