from typing import Tuple, List


def evaluate_wind_risk(
    wind_speed_kmh: float,
    context: str = "general"
) -> Tuple[str, List[str], str]:
    """
    Evaluates wind risk:
    - < 20 km/h -> LOW
    - 20 - 40 km/h -> MODERATE
    - > 40 km/h -> HIGH
    """
    reasons = []

    if wind_speed_kmh < 20.0:
        level = "LOW"
        reasons.append(f"Calm to light wind speeds ({wind_speed_kmh} km/h).")
        rec = "Wind conditions are calm and normal."
    elif 20.0 <= wind_speed_kmh <= 40.0:
        level = "MODERATE"
        reasons.append(f"Breezy to moderate winds ({wind_speed_kmh} km/h).")
        rec = "Secure lightweight loose outdoor objects."
    else:
        level = "HIGH"
        reasons.append(f"Strong wind gusts ({wind_speed_kmh} km/h).")
        rec = "High wind hazard. Avoid standing near tall trees, weak temporary structures, or loose billboards."

    if context == "agriculture" and wind_speed_kmh > 15.0:
        rec = "Avoid crop spraying due to wind drift hazard, even if rain probability is low."

    return level, reasons, rec
