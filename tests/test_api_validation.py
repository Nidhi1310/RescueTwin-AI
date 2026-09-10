from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_route_rejects_unknown_location() -> None:
    response = client.get("/api/v1/route", params={"start_id": "missing", "end_id": "zone-01"})
    assert response.status_code == 404
    assert "Unknown district location" in response.json()["detail"]


def test_team_rejects_unknown_incident_zone() -> None:
    response = client.get("/api/v1/recommendations/team", params={"incident_zone_id": "missing"})
    assert response.status_code == 404
    assert "Unknown incident zone" in response.json()["detail"]


def test_decision_engine_rejects_invalid_drainage_score() -> None:
    response = client.post(
        "/api/v1/decision-engine",
        data={"incident_zone_id": "zone-01", "rainfall_mm": 50, "elevation_m": 72, "drainage_score": 11, "previous_water_level_m": 1.5},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
