import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_current_weather_endpoint():
    response = client.get("/api/weather/current?location=Amritsar")
    assert response.status_code == 200
    data = response.json()
    assert "Amritsar" in data["location"]
    assert "temperature_c" in data
    assert "rain_probability" in data


def test_weather_query_endpoint():
    payload = {
        "query": "Kal Amritsar mein baarish hogi?",
        "location": "Amritsar"
    }
    response = client.post("/api/weather/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Amritsar" in data["resolved_location"]
    assert data["risk_evaluation"]["risk_level"] in ["LOW", "MODERATE", "HIGH", "SEVERE"]
    assert "grounded_answer" in data
