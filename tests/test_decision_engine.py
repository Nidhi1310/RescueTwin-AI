"""Tests for the unified decision engine API."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.entities import TeamStatus
from app.services.district_service import get_district


def test_decision_engine_bundle_consistency():
    """Verify that the decision engine bundle uses the same scenario for all outputs and handles routing consistently."""
    with TestClient(app) as client:
        payload = {
            "incident_zone_id": "zone-01",
            "rainfall_mm": 200.0,
            "elevation_m": 85.0,
            "drainage_score": 3,
            "previous_water_level_m": 1.5,
            "required_specialty": "water_rescue",
        }
        response = client.post("/api/v1/decision-engine", data=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # 1. Prediction returned
        assert "prediction" in data
        severity = data["prediction"]["predicted_flood_severity"]
        
        # 2. Simulation uses the same scenario
        assert "simulation" in data
        expected_scenario = "moderate"
        if severity >= 75:
            expected_scenario = "extreme"
        elif severity >= 40:
            expected_scenario = "severe"
            
        assert data["simulation"]["scenario"].lower() == expected_scenario
        
        # Extract blocked roads from simulation to verify routes
        blocked_road_ids = {r["road_id"] for r in data["simulation"]["blocked_roads"]}
        
        # 3. Hospital routing verification
        if data["hospital_recommendation"]["status"] == "success":
            assert data["hospital_recommendation"]["scenario"].lower() == expected_scenario
            assert data["hospital_route"] is not None
            assert data["hospital_route"]["status"] == "success"
            
        # 4. Shelter routing verification
        if data["shelter_recommendation"]["status"] == "success":
            assert data["shelter_recommendation"]["scenario"].lower() == expected_scenario
            assert data["shelter_route"] is not None
        
        # 5. Team allocation verification
        if data["team_allocation"]["status"] == "success":
            assert data["team_allocation"]["scenario"].lower() == expected_scenario
            assert data["team_route"] is not None
            # The required specialty was requested
            assert data["team_allocation"]["required_specialty"] == "water_rescue"


def test_decision_engine_with_image_upload():
    """Verify that uploading an image successfully populates the damage assessment field."""
    with TestClient(app) as client:
        # Valid dummy jpeg
        dummy_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        
        data = {
            "incident_zone_id": "zone-02",
            "rainfall_mm": 150.0,
            "elevation_m": 70.0,
            "drainage_score": 5,
            "previous_water_level_m": 1.0,
        }
        
        files = {
            "file": ("test_incident.jpg", dummy_jpeg, "image/jpeg")
        }
        
        response = client.post("/api/v1/decision-engine", data=data, files=files)
        
        assert response.status_code == 200
        json_data = response.json()
        
        assert "damage_assessment" in json_data
        assert json_data["damage_assessment"] is not None
        assert json_data["damage_assessment"]["filename"] == "test_incident.jpg"
        assert "damage_level" in json_data["damage_assessment"]
