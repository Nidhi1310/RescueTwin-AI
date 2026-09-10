from fastapi.testclient import TestClient

from app.main import app
from app.services.district_service import get_district
from app.services.flood_simulation import simulate_flood
from app.models.simulation import RainfallScenario

client = TestClient(app)


def test_simulation_is_deterministic_for_each_scenario() -> None:
    district = get_district()
    for scenario in RainfallScenario:
        assert simulate_flood(district, scenario).model_dump() == simulate_flood(district, scenario).model_dump()


def test_decision_engine_returns_consistent_incident_context() -> None:
    response = client.post(
        "/api/v1/decision-engine",
        data={"incident_zone_id": "zone-01", "rainfall_mm": 50, "elevation_m": 72, "drainage_score": 3, "previous_water_level_m": 1.5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["incident_zone_id"] == "zone-01"
    assert payload["simulation"]["scenario"] in {"moderate", "severe", "extreme"}
    for key in ("hospital_recommendation", "shelter_recommendation", "team_allocation"):
        assert key in payload


def test_report_endpoint_rejects_malformed_payload() -> None:
    response = client.post("/api/v1/generate-report", json={"incident_zone_id": "zone-01"})
    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
