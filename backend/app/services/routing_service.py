"""Routing engine for calculating safe paths in the district.

The routing graph is **immutable** once built and shared between threads.
Recommendation services never rebuild it; they only read it.  A graph is
cached per district object, so concurrent requests can never observe a
half-built or cleared graph.
"""

from __future__ import annotations

import heapq
import math
import threading
from dataclasses import dataclass

from app.models.district import DistrictProfile
from app.models.entities import GeoPoint


@dataclass(frozen=True)
class _Edge:
    to: str
    length_km: float
    road_id: str | None  # None => virtual link between a facility/team and its home zone
    geometry: tuple[GeoPoint, ...]


@dataclass(frozen=True)
class RoutingGraph:
    """Read-only adjacency list plus node coordinates."""

    adjacency: dict[str, tuple[_Edge, ...]]
    locations: dict[str, GeoPoint]


_lock = threading.Lock()
_graphs: dict[int, tuple[DistrictProfile, RoutingGraph]] = {}
_default_graph: RoutingGraph | None = None
_MAX_CACHED_GRAPHS = 8


def _construct_graph(district: DistrictProfile) -> RoutingGraph:
    adjacency: dict[str, list[_Edge]] = {}
    locations: dict[str, GeoPoint] = {}

    def add(a: str, edge: _Edge) -> None:
        adjacency.setdefault(a, []).append(edge)

    for zone in district.zones:
        locations[zone.id] = zone.center
        adjacency.setdefault(zone.id, [])

    for facility in (*district.hospitals, *district.shelters):
        locations[facility.id] = facility.location
        add(facility.id, _Edge(facility.zone_id, 0.0, None, ()))
        add(facility.zone_id, _Edge(facility.id, 0.0, None, ()))

    for team in district.rescue_teams:
        locations[team.id] = team.location
        add(team.id, _Edge(team.home_zone_id, 0.0, None, ()))
        add(team.home_zone_id, _Edge(team.id, 0.0, None, ()))

    # Parallel roads between the same zones are kept as separate edges.
    for road in district.roads:
        add(road.from_zone_id, _Edge(road.to_zone_id, road.length_km, road.id, tuple(road.geometry)))
        add(road.to_zone_id, _Edge(road.from_zone_id, road.length_km, road.id, tuple(reversed(road.geometry))))

    return RoutingGraph(
        adjacency={node: tuple(edges) for node, edges in adjacency.items()},
        locations=locations,
    )


def get_routing_graph(district: DistrictProfile | None = None) -> RoutingGraph:
    """Return the (cached, immutable) graph for a district.

    With no argument the process-wide default graph is returned, built lazily
    from the static district profile.
    """

    global _default_graph
    if district is None:
        graph = _default_graph
        if graph is None:
            from app.services.district_service import get_district

            graph = get_routing_graph(get_district())
            with _lock:
                if _default_graph is None:
                    _default_graph = graph
                graph = _default_graph
        return graph

    key = id(district)
    with _lock:
        cached = _graphs.get(key)
        if cached is not None and cached[0] is district:
            return cached[1]
    graph = _construct_graph(district)
    with _lock:
        if len(_graphs) >= _MAX_CACHED_GRAPHS:
            _graphs.pop(next(iter(_graphs)))
        _graphs[key] = (district, graph)  # holding the district prevents id() reuse
    return graph


def build_routing_graph(district: DistrictProfile) -> None:
    """Pre-build the graph for a district and make it the default.

    Safe to call at any time: the new graph is built completely before it is
    published with a single atomic swap, and existing readers keep the graph
    object they already hold.
    """

    global _default_graph
    graph = get_routing_graph(district)
    with _lock:
        _default_graph = graph


def straight_line_km(a: GeoPoint, b: GeoPoint) -> float:
    """Great-circle distance, used only for non-road (boat/air) fallbacks."""

    radius_km = 6371.0088
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    d_lat = lat2 - lat1
    d_lon = math.radians(b.longitude - a.longitude)
    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(h))


def location_of(entity_id: str, district: DistrictProfile | None = None) -> GeoPoint | None:
    return get_routing_graph(district).locations.get(entity_id)


def is_zone_isolated(zone_id: str, blocked_road_ids: set[str], district: DistrictProfile | None = None) -> bool:
    """True when every road touching the zone is blocked (or it has none)."""

    graph = get_routing_graph(district)
    roads = [edge for edge in graph.adjacency.get(zone_id, ()) if edge.road_id is not None]
    return all(edge.road_id in blocked_road_ids for edge in roads)


def find_safe_route(
    start_id: str,
    end_id: str,
    blocked_road_ids: set[str],
    district: DistrictProfile | None = None,
) -> tuple[list[GeoPoint], float]:
    """Find the shortest path avoiding blocked roads.

    Returns ``([], 0.0)`` when no route exists.  A route from a location to
    itself is a valid single-point route of length 0.
    """

    graph = get_routing_graph(district)
    if start_id not in graph.locations or end_id not in graph.locations:
        return [], 0.0
    if start_id == end_id:
        return [graph.locations[start_id]], 0.0

    distances: dict[str, float] = {start_id: 0.0}
    previous: dict[str, tuple[str, _Edge]] = {}
    queue: list[tuple[float, str]] = [(0.0, start_id)]

    while queue:
        current_distance, node = heapq.heappop(queue)
        if current_distance > distances.get(node, math.inf):
            continue
        if node == end_id:
            break
        for edge in graph.adjacency.get(node, ()):
            if edge.road_id is not None and edge.road_id in blocked_road_ids:
                continue
            candidate = current_distance + edge.length_km
            if candidate < distances.get(edge.to, math.inf):
                distances[edge.to] = candidate
                previous[edge.to] = (node, edge)
                heapq.heappush(queue, (candidate, edge.to))

    if end_id not in distances:
        return [], 0.0

    steps: list[tuple[str, str, _Edge]] = []
    cursor = end_id
    while cursor != start_id:
        parent, edge = previous[cursor]
        steps.append((parent, cursor, edge))
        cursor = parent
    steps.reverse()

    path: list[GeoPoint] = []
    for origin, target, edge in steps:
        if edge.road_id is None:
            if not path:
                path.append(graph.locations[origin])
            path.append(graph.locations[target])
        elif not path:
            path.extend(edge.geometry)
        else:
            path.extend(edge.geometry[1:])
    return path, distances[end_id]
