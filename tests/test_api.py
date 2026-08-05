"""Smoke tests for the initial public API contract."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "rescuetwin-api"}


def test_district_endpoint_returns_required_fictional_assets() -> None:
    response = client.get("/api/v1/district")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["name"] == "Sundarpur District"
    assert len(payload["zones"]) == 10
    assert len(payload["roads"]) == 30
    assert len(payload["hospitals"]) == 2
    assert len(payload["shelters"]) == 3
    assert len(payload["rescue_teams"]) == 5


def test_simulation_endpoint_returns_a_typed_json_result() -> None:
    response = client.get("/api/v1/simulate", params={"scenario": "severe"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["scenario"] == "severe"
    assert isinstance(payload["severity_score"], float)
    assert len(payload["zone_impacts"]) == 10
    assert "lower elevations" in payload["explanation"]
