"""Day 21 regression coverage for core backend behavior and API contracts."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.simulation import RainfallScenario
from app.services.district_service import get_district
from app.services.flood_simulation import simulate_flood
from app.services.routing_service import build_routing_graph, find_safe_route

client = TestClient(app)


def test_simulation_is_repeatable_for_every_scenario() -> None:
    """The deterministic digital twin must return identical results for repeated inputs."""
    district = get_district()

    for scenario in RainfallScenario:
        first = simulate_flood(district, scenario)
        second = simulate_flood(district, scenario)
        assert first == second


def test_simulation_severity_and_blocked_roads_are_monotonic() -> None:
    """Increasing rainfall scenarios should not reduce overall severity or blocked roads."""
    district = get_district()
    results = [simulate_flood(district, scenario) for scenario in RainfallScenario]

    assert results[0].severity_score <= results[1].severity_score <= results[2].severity_score
    assert len(results[0].blocked_roads) <= len(results[1].blocked_roads) <= len(results[2].blocked_roads)


def test_route_result_is_repeatable() -> None:
    """The same routing request should produce the same safe path and distance."""
    district = get_district()
    build_routing_graph(district)

    first = find_safe_route("zone-01", "zone-10", set())
    second = find_safe_route("zone-01", "zone-10", set())

    assert first == second
    assert first[0]
    assert first[1] > 0


def test_route_rejects_unknown_destination_at_api_boundary() -> None:
    """Unknown operational locations must remain a controlled client error."""
    response = client.get(
        "/api/v1/route",
        params={"start_id": "team-01", "end_id": "does-not-exist", "scenario": "moderate"},
    )

    assert response.status_code == 404
    assert "Unknown operational location id" in response.json()["detail"]


def test_simulation_api_rejects_invalid_scenario() -> None:
    """Invalid scenario values must not silently fall back to a valid scenario."""
    response = client.get("/api/v1/simulate", params={"scenario": "invalid"})

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_prediction_api_returns_stable_contract() -> None:
    """Prediction responses expose bounded severity, confidence, and explanation fields."""
    payload = {
        "rainfall_mm": 180.0,
        "elevation_m": 72.0,
        "drainage_score": 3,
        "previous_water_level_m": 1.5,
    }

    first = client.post("/api/v1/predict", json=payload)
    second = client.post("/api/v1/predict", json=payload)

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    result = first.json()
    assert 0 <= result["predicted_flood_severity"] <= 100
    assert result["confidence"] in {"low", "medium", "high"}
    assert result["explanation"]


def test_report_generation_preserves_core_incident_details() -> None:
    """Generated reports must remain readable and tied to the supplied decision bundle."""
    from app.services.decision_engine import generate_decision_bundle

    decision = generate_decision_bundle(
        district=get_district(),
        incident_zone_id="zone-03",
        rainfall_mm=210.0,
        elevation_m=65.0,
        drainage_score=3,
        previous_water_level_m=2.0,
        required_specialty="medical",
    )

    response = client.post("/api/v1/generate-report", json=decision.model_dump())

    assert response.status_code == 200
    report = response.json()["report_content"]
    assert report.startswith("RescueTwin AI Incident Report")
    assert "zone-03" in report
    assert str(decision.prediction.predicted_flood_severity) in report
    assert decision.prediction.confidence.upper() in report
