import pytest
from app.risk.engine import risk_engine
from app.risk.rain_rules import evaluate_rain_risk
from app.risk.wind_rules import evaluate_wind_risk
from app.risk.visibility_rules import evaluate_visibility_risk


def test_rain_rules_thresholds():
    lvl, reasons, rec = evaluate_rain_risk(rain_probability=20.0)
    assert lvl == "LOW"

    lvl, reasons, rec = evaluate_rain_risk(rain_probability=45.0)
    assert lvl == "MODERATE"

    lvl, reasons, rec = evaluate_rain_risk(rain_probability=75.0)
    assert lvl == "HIGH"


def test_agriculture_spraying_context():
    lvl, reasons, rec = evaluate_rain_risk(rain_probability=65.0, context="agriculture")
    assert lvl == "HIGH"
    assert "Unsuitable for pesticide" in rec


def test_risk_engine_evaluation():
    weather_data = {
        "rain_probability": 65.0,
        "precipitation_mm": 12.0,
        "wind_speed_kmh": 15.0,
        "visibility_km": 8.0,
        "temperature_c": 31.0
    }
    result = risk_engine.evaluate(weather_data, warnings=[], context="general")
    assert result.risk_level == "HIGH"
    assert len(result.reasons) > 0
