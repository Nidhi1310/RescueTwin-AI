"""Tests for deterministic flood simulation behavior."""

from app.models.simulation import RainfallScenario
from app.services.district_service import get_district
from app.services.flood_simulation import SCENARIO_CONFIGURATIONS, calculate_zone_severity, simulate_flood


def test_all_rainfall_scenarios_are_deterministic_and_increase_severity() -> None:
    district = get_district()
    moderate = simulate_flood(district, RainfallScenario.MODERATE)
    severe = simulate_flood(district, RainfallScenario.SEVERE)
    extreme = simulate_flood(district, RainfallScenario.EXTREME)

    assert moderate == simulate_flood(district, RainfallScenario.MODERATE)
    assert moderate.scenario is RainfallScenario.MODERATE
    assert severe.scenario is RainfallScenario.SEVERE
    assert extreme.scenario is RainfallScenario.EXTREME
    assert moderate.severity_score < severe.severity_score < extreme.severity_score
    assert len(moderate.zone_impacts) == 10


def test_low_elevation_poorly_drained_zone_is_more_severe_than_high_ground() -> None:
    district = get_district()
    riverbend = next(zone for zone in district.zones if zone.id == "zone-01")
    greenridge = next(zone for zone in district.zones if zone.id == "zone-09")
    intensity = SCENARIO_CONFIGURATIONS[RainfallScenario.SEVERE].rainfall_intensity

    assert riverbend.elevation_m < greenridge.elevation_m
    assert riverbend.drainage_score < greenridge.drainage_score
    assert calculate_zone_severity(riverbend, intensity) > calculate_zone_severity(greenridge, intensity)


def test_simulation_marks_affected_zones_and_blocked_roads() -> None:
    result = simulate_flood(get_district(), RainfallScenario.EXTREME)

    assert result.affected_zones
    assert result.blocked_roads
    assert all(impact.affected for impact in result.affected_zones)
