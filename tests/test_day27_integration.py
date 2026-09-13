"""Day 27 end-to-end integration coverage for the primary incident workflow."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.district_service import get_district

client = TestClient(app)


def _decision_form(zone_id: str, scenario: str) -> dict[str, str]:
    rainfall = {"moderate": "50.0", "severe": "100.0", "extreme": "200.0"}[scenario]
    zone = next(zone for zone in get_district().zones if zone.id == zone_id)
    return {
        "incident_zone_id": zone_id,
        "rainfall_mm": rainfall,
        "elevation_m": str(zone.elevation_m),
        "drainage_score": str(zone.drainage_score),
        "previous_water_level_m": "1.5",
    }


def test_scenario_to_report_flow_stays_on_one_incident_state() -> None:
    """Each scenario must produce a synchronized decision bundle and report."""
    district = get_district()
    zone_id = district.zones[2].id

    for scenario in ("moderate", "severe", "extreme"):
        simulation = client.get("/api/v1/simulate", params={"scenario": scenario})
        assert simulation.status_code == 200
        simulation_payload = simulation.json()

        decision_response = client.post(
            "/api/v1/decision-engine",
            data=_decision_form(zone_id, scenario),
        )
        assert decision_response.status_code == 200
        decision = decision_response.json()

        assert decision["incident_zone_id"] == zone_id
        assert decision["simulation"] == simulation_payload

        report_response = client.post("/api/v1/generate-report", json=decision)
        assert report_response.status_code == 200
        report = report_response.json()["report_content"]

        assert zone_id in report
        assert str(decision["prediction"]["predicted_flood_severity"]) in report
        assert decision["prediction"]["confidence"].upper() in report


def test_decision_bundle_references_only_current_district_entities() -> None:
    """Recommendations and routes must remain valid against the same district snapshot."""
    district = get_district()
    zone_ids = {zone.id for zone in district.zones}
    hospital_ids = {hospital.id for hospital in district.hospitals}
    shelter_ids = {shelter.id for shelter in district.shelters}
    team_ids = {team.id for team in district.rescue_teams}

    response = client.post(
        "/api/v1/decision-engine",
        data=_decision_form(district.zones[2].id, "severe"),
    )
    assert response.status_code == 200
    decision = response.json()

    assert decision["incident_zone_id"] in zone_ids

    hospital = decision["hospital_recommendation"]["selected_hospital"]
    if hospital:
        assert hospital["hospital_id"] in hospital_ids
    if decision["hospital_route"]:
        assert decision["hospital_route"]["status"] == "success"

    shelter = decision["shelter_recommendation"]["selected_shelter"]
    if shelter:
        assert shelter["shelter_id"] in shelter_ids
    if decision["shelter_route"]:
        assert decision["shelter_route"]["status"] == "success"

    team = decision["team_allocation"]["selected_team"]
    if team:
        assert team["team_id"] in team_ids
    if decision["team_route"]:
        assert decision["team_route"]["status"] == "success"
