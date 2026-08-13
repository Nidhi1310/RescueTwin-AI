"""Routing engine for calculating safe paths in the district."""

import heapq
from collections import defaultdict

from app.models.district import DistrictProfile
from app.models.entities import GeoPoint


# Global state for the routing graph (built once on startup)
_road_graph: dict[str, dict[str, dict]] = defaultdict(dict)
_locations: dict[str, GeoPoint] = {}


def build_routing_graph(district: DistrictProfile) -> None:
    """Build the static routing graph from the district profile."""
    _road_graph.clear()
    _locations.clear()

    # Add all entities to locations
    for zone in district.zones:
        _locations[zone.id] = zone.center
    
    for facility in district.hospitals + district.shelters:
        _locations[facility.id] = facility.location
        # Zero-distance link between facility and its home zone
        _road_graph[facility.id][facility.zone_id] = {"length_km": 0.0, "road_id": None}
        _road_graph[facility.zone_id][facility.id] = {"length_km": 0.0, "road_id": None}

    for team in district.rescue_teams:
        _locations[team.id] = team.location
        # Zero-distance link between team and its home zone
        _road_graph[team.id][team.home_zone_id] = {"length_km": 0.0, "road_id": None}
        _road_graph[team.home_zone_id][team.id] = {"length_km": 0.0, "road_id": None}

    # Add roads as bidirectional edges
    for road in district.roads:
        _road_graph[road.from_zone_id][road.to_zone_id] = {
            "length_km": road.length_km,
            "road_id": road.id,
            "geometry": road.geometry,
        }
        _road_graph[road.to_zone_id][road.from_zone_id] = {
            "length_km": road.length_km,
            "road_id": road.id,
            "geometry": tuple(reversed(road.geometry)),
        }


def find_safe_route(
    start_id: str, end_id: str, blocked_road_ids: set[str]
) -> tuple[list[GeoPoint], float]:
    """Find the shortest path avoiding blocked roads."""
    if start_id not in _locations or end_id not in _locations:
        return [], 0.0

    distances = {node: float("inf") for node in _locations}
    distances[start_id] = 0.0
    previous: dict[str, str | None] = {node: None for node in _locations}

    pq: list[tuple[float, str]] = [(0.0, start_id)]

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_distance > distances[current_node]:
            continue

        if current_node == end_id:
            break

        for neighbor, edge_data in _road_graph[current_node].items():
            if edge_data["road_id"] in blocked_road_ids:
                continue

            distance = current_distance + edge_data["length_km"]

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    if distances[end_id] == float("inf"):
        return [], 0.0

    # Reconstruct path nodes
    path_nodes = []
    current: str | None = end_id
    while current is not None:
        path_nodes.append(current)
        current = previous[current]
    path_nodes.reverse()

    # Reconstruct exact geometry along the path
    path_coords = []
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i + 1]
        edge = _road_graph[u][v]

        if edge["road_id"] is None:
            # Facility/Team to zone virtual edge
            if not path_coords:
                path_coords.append(_locations[u])
            path_coords.append(_locations[v])
        else:
            geom = list(edge["geometry"])
            if not path_coords:
                path_coords.extend(geom)
            else:
                path_coords.extend(geom[1:])

    return path_coords, distances[end_id]
