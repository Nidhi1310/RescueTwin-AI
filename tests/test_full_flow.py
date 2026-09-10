from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_scenario_to_report_flow_stays_synchronized() -> None:
    simulation = client.get("/api/v1/simulate", params={"scenario": "extreme"})
    assert simulation.status_code == 200

    decision = client.post(
        "/api/v1/decision-engine",
        data={"incident_zone_id": "zone-01", "rainfall_mm": 200, "elevation_m": 72, "drainage_score": 3, "previous_water_level_m": 1.5},
    )
    assert decision.status_code == 200
    payload = decision.json()
    assert payload["incident_zone_id"] == "zone-01"
    assert payload["simulation"]["scenario"] == "extreme"

    report = client.post("/api/v1/generate-report", json=payload)
    assert report.status_code == 200
    assert "zone-01" in report.json()["report_content"]
