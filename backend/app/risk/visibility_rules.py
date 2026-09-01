from typing import Tuple, List


def evaluate_visibility_risk(
    visibility_km: float,
    context: str = "general"
) -> Tuple[str, List[str], str]:
    """
    Evaluates visibility risk:
    - > 5.0 km -> LOW
    - 2.0 - 5.0 km -> MODERATE
    - < 2.0 km -> HIGH / SEVERE (Fog hazard)
    """
    reasons = []

    if visibility_km >= 5.0:
        level = "LOW"
        reasons.append(f"Good visibility ({visibility_km} km).")
        rec = "Visibility conditions are clear."
    elif 2.0 <= visibility_km < 5.0:
        level = "MODERATE"
        reasons.append(f"Reduced visibility ({visibility_km} km) due to mist, haze, or light fog.")
        rec = "Drive with headlights on low beam and maintain safe following distances."
    else:
        level = "HIGH"
        reasons.append(f"Poor visibility ({visibility_km} km) due to dense fog or heavy downpour.")
        rec = "High travel hazard. Use fog lights, reduce highway speeds significantly, and delay non-essential night/early morning trips."

    return level, reasons, rec
