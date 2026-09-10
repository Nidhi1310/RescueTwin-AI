from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_route_rejects_unknown_locations() -> None:
    response = client.get(
        "/api/v1/route",
        params={"start_id": "unknown", "end_id": "shelter-1"},
    )
    assert response.status_code == 404
    assert "Unknown operational location id" in response.json()["detail"]


def test_team_recommendation_rejects_unknown_zone() -> None:
    response = client.get(
        "/api/v1/recommendations/team",
        params={"incident_zone_id": "unknown"},
    )
    assert response.status_code == 404
    assert "Unknown zone id" in response.json()["detail"]


def test_prediction_validation_has_structured_error() -> None:
    response = client.post(
        "/api/v1/predict",
        json={
            "rainfall_mm": -1,
            "elevation_m": 80,
            "drainage_score": 3,
            "previous_water_level_m": 1.5,
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_decision_engine_rejects_invalid_environmental_values() -> None:
    response = client.post(
        "/api/v1/decision-engine",
        data={
            "incident_zone_id": "zone-1",
            "rainfall_mm": "500",
            "elevation_m": "80",
            "drainage_score": "3",
            "previous_water_level_m": "1.5",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_empty_damage_upload_returns_bad_request() -> None:
    response = client.post(
        "/api/v1/assess-damage",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Empty file uploaded."
