"""Deterministic flood simulation based on district elevation and drainage data."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.district import DistrictProfile
from app.models.entities import FloodZone
from app.models.simulation import BlockedRoad, FloodSimulationResult, RainfallScenario, ZoneFloodImpact


@dataclass(frozen=True)
class ScenarioConfiguration:
    """Tunable, explicit weights for a rainfall scenario."""

    rainfall_intensity: float
    affected_threshold: float
    road_block_threshold: float


SCENARIO_CONFIGURATIONS: dict[RainfallScenario, ScenarioConfiguration] = {
    RainfallScenario.MODERATE: ScenarioConfiguration(0.45, 35.0, 48.0),
    RainfallScenario.SEVERE: ScenarioConfiguration(0.70, 35.0, 65.0),
    RainfallScenario.EXTREME: ScenarioConfiguration(0.95, 35.0, 82.0),
}

_ELEVATION_REFERENCE_M = 100.0


def calculate_zone_severity(zone: FloodZone, rainfall_intensity: float) -> float:
    """Calculate a repeatable 0-100 flood score for one zone.

    Lower elevations and lower drainage scores increase the outcome.  The
    reference elevation keeps the fictional district's score scale stable.
    """

    elevation_exposure = max(0.0, min(1.0, (_ELEVATION_REFERENCE_M - zone.elevation_m) / 35.0))
    drainage_exposure = (10 - zone.drainage_score) / 9
    susceptibility = 0.45 + (0.30 * elevation_exposure) + (0.25 * drainage_exposure)
    return round(min(100.0, rainfall_intensity * 100 * susceptibility), 1)


def simulate_flood(district: DistrictProfile, scenario: RainfallScenario) -> FloodSimulationResult:
    """Generate an entirely deterministic flood result for a district scenario."""

    configuration = SCENARIO_CONFIGURATIONS[scenario]
    zone_impacts = tuple(
        ZoneFloodImpact(
            zone_id=zone.id,
            zone_name=zone.name,
            severity_score=calculate_zone_severity(zone, configuration.rainfall_intensity),
            affected=calculate_zone_severity(zone, configuration.rainfall_intensity) >= configuration.affected_threshold,
        )
        for zone in district.zones
    )
    impacts_by_zone_id = {impact.zone_id: impact for impact in zone_impacts}
    affected_zones = tuple(impact for impact in zone_impacts if impact.affected)
    blocked_roads = tuple(
        BlockedRoad(
            road_id=road.id,
            road_name=road.name,
            from_zone_id=road.from_zone_id,
            to_zone_id=road.to_zone_id,
            reason=(
                "Adjacent zone flood severity meets the "
                f"{scenario.value} road-closure threshold."
            ),
        )
        for road in district.roads
        if max(
            impacts_by_zone_id[road.from_zone_id].severity_score,
            impacts_by_zone_id[road.to_zone_id].severity_score,
        ) >= configuration.road_block_threshold
    )
    district_severity = round(sum(impact.severity_score for impact in zone_impacts) / len(zone_impacts), 1)
    explanation = (
        f"The {scenario.value} scenario uses rainfall intensity {configuration.rainfall_intensity:.2f}; "
        "lower elevations and weaker drainage produce higher deterministic flood scores."
    )
    return FloodSimulationResult(
        scenario=scenario,
        rainfall_intensity=configuration.rainfall_intensity,
        severity_score=district_severity,
        zone_impacts=zone_impacts,
        affected_zones=affected_zones,
        blocked_roads=blocked_roads,
        explanation=explanation,
    )
