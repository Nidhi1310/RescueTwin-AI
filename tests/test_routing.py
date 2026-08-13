"""Tests for the routing engine."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.district_service import get_district
from app.services.routing_service import build_routing_graph, find_safe_route


def test_build_routing_graph():
    """Verify the routing graph initializes properly."""
    district = get_district()
    build_routing_graph(district)
    
    # Internal state check to ensure nodes are populated
    from app.services.routing_service import _road_graph, _locations
    assert len(_road_graph) > 0
    assert len(_locations) > 0
    assert district.zones[0].id in _locations


def test_find_safe_route_clear_path():
    """Verify route computation without blocked roads."""
    district = get_district()
    build_routing_graph(district)
    
    start_zone = district.zones[0].id
    end_zone = district.zones[-1].id
    
    path, dist = find_safe_route(start_zone, end_zone, blocked_road_ids=set())
    
    assert dist > 0.0
    assert len(path) >= 2


def test_find_safe_route_blocked_path():
    """Verify route computation respects blocked roads."""
    district = get_district()
    build_routing_graph(district)
    
    start_zone = district.zones[0].id
    end_zone = district.zones[-1].id
    
    # First find a clear route to identify an edge we can block
    clear_path, clear_dist = find_safe_route(start_zone, end_zone, set())
    assert clear_dist > 0
    
    # Block all roads to force no route available
    all_road_ids = {road.id for road in district.roads}
    blocked_path, blocked_dist = find_safe_route(start_zone, end_zone, all_road_ids)
    
    assert blocked_dist == 0.0
    assert len(blocked_path) == 0


def test_integration_simulate_to_routing():
    """End-to-end test verifying Simulation -> Blocked Roads -> Routing."""
    district = get_district()
    build_routing_graph(district)
    
    with TestClient(app) as client:
        # We know team-01 and shelter-01 exist from static data
        response = client.get("/api/v1/route?start_id=team-01&end_id=shelter-01&scenario=extreme")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ("success", "no_route_available")
        assert "distance_km" in data
        assert "path" in data
