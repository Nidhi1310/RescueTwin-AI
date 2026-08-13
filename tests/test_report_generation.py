"""Tests for the incident report generation API."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.decision_engine import DecisionEngineResponse
from app.services.decision_engine import generate_decision_bundle
from app.services.district_service import get_district


def test_generate_incident_report():
    """Verify that a valid decision engine bundle can be parsed into a readable text report."""
    
    # Generate a bundle deterministically using the decision engine directly
    district = get_district()
    decision = generate_decision_bundle(
        district=district,
        incident_zone_id="zone-03",
        rainfall_mm=210.0,
        elevation_m=65.0,
        drainage_score=3,
        previous_water_level_m=2.0,
        required_specialty="medical",
    )
    
    # Now test the endpoint
    with TestClient(app) as client:
        # Pydantic's dict() or model_dump() handles nested JSON serialization 
        # But we must convert it to a serializable dict (fastapi client json=... does this)
        response = client.post("/api/v1/generate-report", json=decision.model_dump())
        
        assert response.status_code == 200
        data = response.json()
        
        assert "report_content" in data
        assert "generated_at" in data
        
        report = data["report_content"]
        
        # Verify it includes some core templated text
        assert "RescueTwin AI Incident Report" in report
        assert "zone-03" in report
        
        # Verify it includes the predicted severity and confidence
        severity = decision.prediction.predicted_flood_severity
        assert str(severity) in report
        assert decision.prediction.confidence.upper() in report
        
        # Verify hospital, shelter, team names exist if they were selected
        if decision.hospital_recommendation.selected_hospital:
            assert decision.hospital_recommendation.selected_hospital.hospital_name in report
        if decision.shelter_recommendation.selected_shelter:
            assert decision.shelter_recommendation.selected_shelter.shelter_name in report
        if decision.team_allocation.selected_team:
            assert decision.team_allocation.selected_team.team_name in report
