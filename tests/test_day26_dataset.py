"""Day 26 regression coverage for fictional district asset coherence."""

from app.services.district_service import get_district


def test_district_asset_references_are_coherent() -> None:
    district = get_district()
    zone_ids = {zone.id for zone in district.zones}

    assert district.metadata.id == "sundarpur"
    assert district.metadata.name == "Sundarpur District"

    for road in district.roads:
        assert road.from_zone_id in zone_ids
        assert road.to_zone_id in zone_ids
        assert road.from_zone_id != road.to_zone_id
        assert road.name.strip()

    for facility in (*district.hospitals, *district.shelters):
        assert facility.zone_id in zone_ids
        assert facility.name.strip()
        assert facility.capacity >= facility.current_occupancy

    for team in district.rescue_teams:
        assert team.home_zone_id in zone_ids
        assert team.name.strip()
        assert team.personnel_count > 0


def test_district_asset_ids_are_unique_and_names_are_nonempty() -> None:
    district = get_district()
    entities = [
        *district.zones,
        *district.roads,
        *district.hospitals,
        *district.shelters,
        *district.rescue_teams,
    ]

    assert len({entity.id for entity in entities}) == len(entities)
    assert all(entity.name.strip() for entity in entities)


def test_district_roads_use_consistent_public_labels() -> None:
    district = get_district()
    road_names = {road.name for road in district.roads}

    assert "Civic Heights–Greenridge Arterial" in road_names
    assert "Old Wharf–Lakshmi Bypass" in road_names
    assert "Riverbend–Canal Link" in road_names
