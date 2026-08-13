"""Tests for explainable hospital selection."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.simulation import RainfallScenario
from app.services.district_service import get_district
from app.services.hospital_recommendation import recommend_hospital


def test_normal_conditions_return_an_explainable_ranked_hospital() -> None:
    result = recommend_hospital(get_district(), "team-01", RainfallScenario.MODERATE)

    assert result.status == "success"
    assert result.selected_hospital is not None
    assert result.ranked_hospitals[0] == result.selected_hospital
    assert result.selected_hospital.available_capacity > 0
    assert "safe-route distance" in result.explanation
    assert result.selected_hospital.rationale


def test_low_capacity_changes_the_selected_hospital() -> None:
    district = get_district()
    constrained_hospital = district.hospitals[0].model_copy(update={"current_occupancy": 179})
    constrained_district = district.model_copy(update={"hospitals": (constrained_hospital, district.hospitals[1])})

    result = recommend_hospital(constrained_district, "team-01", RainfallScenario.MODERATE)

    assert result.status == "success"
    assert result.selected_hospital is not None
    assert result.selected_hospital.hospital_id == "hospital-02"


def test_degraded_conditions_exclude_capacity_and_flood_risk() -> None:
    district = get_district()
    full_hospital = district.hospitals[0].model_copy(update={"current_occupancy": 180})
    high_risk_zone = district.zones[8].model_copy(update={"elevation_m": 60, "drainage_score": 1})
    degraded_district = district.model_copy(
        update={
            "hospitals": (full_hospital, district.hospitals[1]),
            "zones": (*district.zones[:8], high_risk_zone, district.zones[9]),
        }
    )

    result = recommend_hospital(degraded_district, "team-01", RainfallScenario.EXTREME)

    assert result.status == "no_suitable_hospital"
    assert {exclusion.hospital_id for exclusion in result.excluded_hospitals} == {"hospital-01", "hospital-02"}
    assert any("capacity" in exclusion.reason for exclusion in result.excluded_hospitals)
    assert any("flood risk" in exclusion.reason for exclusion in result.excluded_hospitals)


def test_hospital_endpoint_returns_a_structured_response() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/recommendations/hospital",
            params={"start_id": "team-01", "scenario": "severe"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["selected_hospital"]
    assert isinstance(payload["ranked_hospitals"], list)
    assert isinstance(payload["excluded_hospitals"], list)
