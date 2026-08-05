"""Typed models describing deterministic flood-simulation inputs and outputs."""

from __future__ import annotations

from enum import Enum

from pydantic import Field

from .entities import DomainModel


class RainfallScenario(str, Enum):
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


class ZoneFloodImpact(DomainModel):
    """Deterministic flood impact calculated for one district zone."""

    zone_id: str
    zone_name: str
    severity_score: float = Field(ge=0, le=100)
    affected: bool


class BlockedRoad(DomainModel):
    """A road temporarily unavailable because of adjacent flood conditions."""

    road_id: str
    road_name: str
    from_zone_id: str
    to_zone_id: str
    reason: str


class FloodSimulationResult(DomainModel):
    """Complete result returned by the deterministic flood simulator."""

    scenario: RainfallScenario
    rainfall_intensity: float = Field(gt=0, le=1)
    severity_score: float = Field(ge=0, le=100)
    zone_impacts: tuple[ZoneFloodImpact, ...]
    affected_zones: tuple[ZoneFloodImpact, ...]
    blocked_roads: tuple[BlockedRoad, ...]
    explanation: str
