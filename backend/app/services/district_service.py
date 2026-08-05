"""Read-only access to RescueTwin's fictional district dataset."""

from __future__ import annotations

from app.models.district import DistrictMetadata, DistrictProfile
from app.models.entities import Facility, FacilityType, FloodZone, GeoPoint, RescueTeam, Road, TeamStatus


def _point(latitude: float, longitude: float) -> GeoPoint:
    return GeoPoint(latitude=latitude, longitude=longitude)


ZONE_ROWS = (
    ("zone-01", "Riverbend", 25.178, 85.545, 72, 3, 18200, "Low-lying riverbank homes and a market district."),
    ("zone-02", "Old Wharf", 25.174, 85.551, 68, 2, 12400, "Historic warehouses beside the Kosi canal."),
    ("zone-03", "Meadowgate", 25.181, 85.557, 78, 6, 9600, "Mixed residential area with moderate drainage."),
    ("zone-04", "Eastbank", 25.176, 85.563, 74, 4, 15100, "Dense housing near the eastern drainage channel."),
    ("zone-05", "Civic Heights", 25.184, 85.552, 91, 8, 8700, "Elevated civic and commercial precinct."),
    ("zone-06", "Lakshmi Nagar", 25.169, 85.559, 70, 3, 16600, "Crowded neighborhood with narrow access lanes."),
    ("zone-07", "South Fields", 25.164, 85.550, 66, 2, 7400, "Agricultural fringe exposed to canal overflow."),
    ("zone-08", "Station Quarter", 25.171, 85.542, 76, 5, 13900, "Transport hub and nearby apartment blocks."),
    ("zone-09", "Greenridge", 25.188, 85.563, 96, 9, 6200, "High-ground residential area and school campus."),
    ("zone-10", "Canal View", 25.166, 85.567, 69, 3, 10900, "Canal-side settlement with limited evacuation routes."),
)

ZONES = tuple(
    FloodZone(id=zone_id, name=name, center=_point(lat, lon), elevation_m=elevation, drainage_score=drainage,
              population=population, vulnerability_notes=notes)
    for zone_id, name, lat, lon, elevation, drainage, population, notes in ZONE_ROWS
)
_CENTERS = {zone.id: zone.center for zone in ZONES}

ROAD_ROWS = (
    ("road-01", "Riverbend Causeway", "zone-01", "zone-02", 1.1, "arterial"),
    ("road-02", "Canal Market Road", "zone-02", "zone-03", 1.3, "collector"),
    ("road-03", "Meadowgate Avenue", "zone-03", "zone-04", 1.0, "arterial"),
    ("road-04", "Eastbank Link", "zone-04", "zone-10", 1.4, "collector"),
    ("road-05", "Civic Rise", "zone-03", "zone-05", 0.9, "arterial"),
    ("road-06", "Hospital Road", "zone-05", "zone-09", 1.5, "arterial"),
    ("road-07", "Wharf Street", "zone-02", "zone-08", 1.2, "collector"),
    ("road-08", "Station Approach", "zone-08", "zone-01", 0.8, "arterial"),
    ("road-09", "South Connector", "zone-08", "zone-07", 1.4, "collector"),
    ("road-10", "Fields Lane", "zone-07", "zone-06", 1.1, "local"),
    ("road-11", "Lakshmi Main Road", "zone-06", "zone-10", 1.0, "collector"),
    ("road-12", "Canal Embankment", "zone-10", "zone-04", 1.2, "arterial"),
    ("road-13", "Riverside Drive", "zone-01", "zone-05", 1.3, "collector"),
    ("road-14", "Civic Loop East", "zone-05", "zone-04", 1.2, "arterial"),
    ("road-15", "Greenridge Way", "zone-05", "zone-09", 1.0, "collector"),
    ("road-16", "North Ridge Road", "zone-03", "zone-09", 1.7, "collector"),
    ("road-17", "Wharf Bypass", "zone-02", "zone-06", 1.6, "arterial"),
    ("road-18", "South Canal Road", "zone-07", "zone-10", 1.5, "collector"),
    ("road-19", "Station-Civic Boulevard", "zone-08", "zone-05", 1.4, "arterial"),
    ("road-20", "Meadow Lane", "zone-01", "zone-03", 1.1, "local"),
    ("road-21", "East Relief Road", "zone-06", "zone-04", 1.3, "arterial"),
    ("road-22", "Hilltop Spur", "zone-04", "zone-09", 1.8, "collector"),
    ("road-23", "Market Ring Road", "zone-02", "zone-05", 1.1, "collector"),
    ("road-24", "Southwest Access", "zone-01", "zone-07", 1.9, "arterial"),
    ("road-25", "Station Service Road", "zone-08", "zone-06", 1.2, "local"),
    ("road-26", "Civic South Link", "zone-05", "zone-06", 1.6, "arterial"),
    ("road-27", "Eastern Perimeter", "zone-03", "zone-10", 1.9, "collector"),
    ("road-28", "River-to-Canal Road", "zone-01", "zone-10", 2.2, "arterial"),
    ("road-29", "Greenridge Descent", "zone-09", "zone-10", 2.0, "collector"),
    ("road-30", "Fields Bypass", "zone-07", "zone-04", 2.1, "arterial"),
)

ROADS = tuple(
    Road(id=road_id, name=name, from_zone_id=start, to_zone_id=end, length_km=length, road_class=road_class,
         geometry=(_CENTERS[start], _CENTERS[end]))
    for road_id, name, start, end, length, road_class in ROAD_ROWS
)

HOSPITALS = (
    Facility(id="hospital-01", name="Civic Heights General Hospital", type=FacilityType.HOSPITAL, zone_id="zone-05",
             location=_point(25.1845, 85.5514), capacity=180, current_occupancy=112,
             services=("emergency", "trauma", "maternity", "ambulance")),
    Facility(id="hospital-02", name="Greenridge Community Hospital", type=FacilityType.HOSPITAL, zone_id="zone-09",
             location=_point(25.1884, 85.5636), capacity=90, current_occupancy=41,
             services=("emergency", "stabilization", "ambulance")),
)
SHELTERS = (
    Facility(id="shelter-01", name="Meadowgate Secondary School", type=FacilityType.SHELTER, zone_id="zone-03",
             location=_point(25.1813, 85.5565), capacity=450, current_occupancy=86,
             services=("meals", "water", "first_aid")),
    Facility(id="shelter-02", name="Civic Heights Sports Hall", type=FacilityType.SHELTER, zone_id="zone-05",
             location=_point(25.1838, 85.5530), capacity=600, current_occupancy=124,
             services=("meals", "water", "accessible_facilities", "first_aid")),
    Facility(id="shelter-03", name="Greenridge Community Center", type=FacilityType.SHELTER, zone_id="zone-09",
             location=_point(25.1875, 85.5624), capacity=320, current_occupancy=39,
             services=("meals", "water", "pet_area")),
)
RESCUE_TEAMS = (
    RescueTeam(id="team-01", name="Delta Water Rescue", home_zone_id="zone-08", location=_point(25.1712, 85.5425), personnel_count=8, specialties=("swift_water", "boat_rescue"), status=TeamStatus.AVAILABLE),
    RescueTeam(id="team-02", name="Civic Medical Response", home_zone_id="zone-05", location=_point(25.1841, 85.5517), personnel_count=6, specialties=("paramedic", "evacuation"), status=TeamStatus.AVAILABLE),
    RescueTeam(id="team-03", name="Eastbank Search Unit", home_zone_id="zone-04", location=_point(25.1764, 85.5627), personnel_count=7, specialties=("search", "rope_rescue"), status=TeamStatus.STANDBY),
    RescueTeam(id="team-04", name="South Fields Evacuation", home_zone_id="zone-07", location=_point(25.1644, 85.5503), personnel_count=9, specialties=("evacuation", "high_clearance_vehicle"), status=TeamStatus.AVAILABLE),
    RescueTeam(id="team-05", name="Greenridge Support Crew", home_zone_id="zone-09", location=_point(25.1881, 85.5631), personnel_count=5, specialties=("logistics", "shelter_support"), status=TeamStatus.STANDBY),
)

DISTRICT = DistrictProfile(
    metadata=DistrictMetadata(id="sundarpur", name="Sundarpur District", region="Bihar", country="India", timezone="Asia/Kolkata",
                              center=_point(25.176, 85.555), description="A fictional river-and-canal district created for RescueTwin AI demonstrations."),
    zones=ZONES, roads=ROADS, hospitals=HOSPITALS, shelters=SHELTERS, rescue_teams=RESCUE_TEAMS,
)


def get_district() -> DistrictProfile:
    """Return the immutable static district profile."""

    return DISTRICT
