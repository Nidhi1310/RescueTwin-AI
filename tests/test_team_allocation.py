"""Tests for the rescue team allocation engine."""

from fastapi.testclient import TestClient

from app.main import app
from app.models.entities import TeamStatus
from app.models.simulation import RainfallScenario
from app.services.district_service import get_district
from app.services.team_allocation import allocate_team


def test_allocate_team_success():
    """Verify team allocation finds an available team."""
    district = get_district()
    # Find an available team to test against
    available_team = next(t for t in district.rescue_teams if t.status == TeamStatus.AVAILABLE)
    incident_zone = "zone-01"
    
    response = allocate_team(district, incident_zone, RainfallScenario.MODERATE)
    
    assert response.status == "success"
    assert response.selected_team is not None
    assert response.selected_team.team_name is not None
    # Ensure ranked teams only include available teams
    for candidate in response.ranked_teams:
        team = next(t for t in district.rescue_teams if t.id == candidate.team_id)
        assert team.status == TeamStatus.AVAILABLE


def test_allocate_team_unavailable_exclusion():
    """Verify that teams not available are correctly excluded."""
    district = get_district()
    incident_zone = "zone-01"
    
    response = allocate_team(district, incident_zone, RainfallScenario.MODERATE)
    
    # Check exclusions for deployed/standby teams
    unavailable_teams = [t for t in district.rescue_teams if t.status != TeamStatus.AVAILABLE]
    
    if unavailable_teams:
        excluded_ids = [ex.team_id for ex in response.excluded_teams]
        for t in unavailable_teams:
            assert t.id in excluded_ids
            # Ensure the reason mentions the status
            exclusion = next(ex for ex in response.excluded_teams if ex.team_id == t.id)
            assert t.status.value in exclusion.reason


def test_allocate_team_specialization_preference():
    """Verify that matching specialization affects the ranking score."""
    district = get_district()
    incident_zone = "zone-01"
    
    # Test without specialty
    response_any = allocate_team(district, incident_zone, RainfallScenario.MODERATE)
    
    # Test with specialty
    # Find an available specialty
    available_team = next(t for t in district.rescue_teams if t.status == TeamStatus.AVAILABLE)
    specialty = available_team.specialties[0]
    
    response_spec = allocate_team(district, incident_zone, RainfallScenario.MODERATE, required_specialty=specialty)
    
    assert response_spec.status == "success"
    
    # The selected team in response_spec should either have the specialty
    # or have won on distance/personnel despite missing it (but scoring logic favors specialty heavily)
    assert response_spec.selected_team.specialty_match is True


def test_api_team_allocation():
    """Test the /recommendations/team endpoint."""
    with TestClient(app) as client:
        response = client.get("/api/v1/recommendations/team?incident_zone_id=zone-01&scenario=moderate&required_specialty=water_rescue")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("success", "no_suitable_team")
        if data["status"] == "success":
            assert "selected_team" in data
            assert data["selected_team"] is not None
            assert "suitability_score" in data["selected_team"]
            
        assert "excluded_teams" in data
