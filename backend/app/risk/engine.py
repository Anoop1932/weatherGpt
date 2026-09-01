import logging
from typing import Dict, Any, List
from app.risk.rain_rules import evaluate_rain_risk
from app.risk.wind_rules import evaluate_wind_risk
from app.risk.visibility_rules import evaluate_visibility_risk
from app.risk.warning_rules import evaluate_warning_risk
from app.schemas.weather_schemas import RiskEvaluation

logger = logging.getLogger(__name__)

# Priority order for risk severity levels
RISK_PRIORITY = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "SEVERE": 4}


class RiskEngine:

    def evaluate(
        self,
        weather_data: Dict[str, Any],
        warnings: List[Dict[str, Any]] = None,
        context: str = "general"
    ) -> RiskEvaluation:
        """
        Executes deterministic risk rules across weather dimensions without LLM modification.
        """
        warnings = warnings or []

        rain_prob = float(weather_data.get("rain_probability", 0.0))
        precip_mm = float(weather_data.get("precipitation_mm", 0.0))
        wind_kmh = float(weather_data.get("wind_speed_kmh", 0.0))
        vis_km = float(weather_data.get("visibility_km", 10.0))
        temp_c = float(weather_data.get("temperature_c", 25.0))

        rain_lvl, rain_reasons, rain_rec = evaluate_rain_risk(rain_prob, precip_mm, context)
        wind_lvl, wind_reasons, wind_rec = evaluate_wind_risk(wind_kmh, context)
        vis_lvl, vis_reasons, vis_rec = evaluate_visibility_risk(vis_km, context)
        warn_lvl, warn_reasons, warn_rec = evaluate_warning_risk(warnings, context)

        # Aggregate highest risk severity
        levels = [rain_lvl, wind_lvl, vis_lvl, warn_lvl]
        highest_level = max(levels, key=lambda l: RISK_PRIORITY.get(l, 1))

        # Collect all active reasons
        all_reasons = []
        if rain_lvl != "LOW":
            all_reasons.extend(rain_reasons)
        if wind_lvl != "LOW":
            all_reasons.extend(wind_reasons)
        if vis_lvl != "LOW":
            all_reasons.extend(vis_reasons)
        if warn_lvl != "LOW":
            all_reasons.extend(warn_reasons)

        if not all_reasons:
            all_reasons = [f"All monitored parameters (rain {rain_prob}%, wind {wind_kmh}km/h, visibility {vis_km}km) remain within safe baseline thresholds."]

        # Formulate primary unified recommendation based on domain context
        primary_rec = rain_rec
        if warn_lvl in ["HIGH", "SEVERE"]:
            primary_rec = warn_rec
        elif wind_lvl == "HIGH" and context != "agriculture":
            primary_rec = wind_rec
        elif vis_lvl == "HIGH" and context == "travel":
            primary_rec = vis_rec

        evidence = {
            "temperature_c": temp_c,
            "rain_probability": rain_prob,
            "precipitation_mm": precip_mm,
            "wind_speed_kmh": wind_kmh,
            "visibility_km": vis_km,
            "active_warning_count": len(warnings),
            "rain_risk_sublevel": rain_lvl,
            "wind_risk_sublevel": wind_lvl,
            "visibility_risk_sublevel": vis_lvl,
            "warning_risk_sublevel": warn_lvl
        }

        return RiskEvaluation(
            risk_level=highest_level,
            category=context,
            reasons=all_reasons,
            recommendation=primary_rec,
            evidence=evidence,
            confidence=weather_data.get("confidence", "HIGH")
        )


risk_engine = RiskEngine()
