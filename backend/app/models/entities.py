"""Core domain entities for the fictional RescueTwin district."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    """Base model that prevents accidental mutation of shared district data."""

    model_config = ConfigDict(frozen=True)


class GeoPoint(DomainModel):
    """A WGS84 point used for map rendering."""

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class FloodZone(DomainModel):
    """An operational flood-management area within the district."""

    id: str = Field(pattern=r"^zone-[0-9]{2}$")
    name: str
    center: GeoPoint
    elevation_m: float = Field(ge=0)
    drainage_score: int = Field(ge=1, le=10)
    population: int = Field(ge=0)
    vulnerability_notes: str


class Road(DomainModel):
    """A road link between two zones; later routing will consume this graph edge."""

    id: str = Field(pattern=r"^road-[0-9]{2}$")
    name: str
    from_zone_id: str = Field(pattern=r"^zone-[0-9]{2}$")
    to_zone_id: str = Field(pattern=r"^zone-[0-9]{2}$")
    length_km: float = Field(gt=0)
    road_class: str
    geometry: tuple[GeoPoint, ...] = Field(min_length=2)


class FacilityType(str, Enum):
    HOSPITAL = "hospital"
    SHELTER = "shelter"


class Facility(DomainModel):
    """A hospital or evacuation shelter available to district operations."""

    id: str = Field(pattern=r"^(hospital|shelter)-[0-9]{2}$")
    name: str
    type: FacilityType
    zone_id: str = Field(pattern=r"^zone-[0-9]{2}$")
    location: GeoPoint
    capacity: int = Field(gt=0)
    current_occupancy: int = Field(ge=0)
    services: tuple[str, ...]


class TeamStatus(str, Enum):
    AVAILABLE = "available"
    DEPLOYED = "deployed"
    STANDBY = "standby"


class RescueTeam(DomainModel):
    """A field team that can be allocated by a future dispatch service."""

    id: str = Field(pattern=r"^team-[0-9]{2}$")
    name: str
    home_zone_id: str = Field(pattern=r"^zone-[0-9]{2}$")
    location: GeoPoint
    personnel_count: int = Field(gt=0)
    specialties: tuple[str, ...]
    status: TeamStatus
