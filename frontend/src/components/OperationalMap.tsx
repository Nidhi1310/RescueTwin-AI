import "leaflet/dist/leaflet.css";
import { useEffect, useMemo } from "react";
import { Circle, CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip, useMap } from "react-leaflet";
import { divIcon } from "leaflet";
import type { LatLngBoundsExpression } from "leaflet";
import type { Facility, FloodSimulationResult, FloodZone, GeoPoint, RescueTeam, RouteResponse } from "../types";

interface OperationalMapProps {
  zones: FloodZone[];
  hospitals: Facility[];
  shelters: Facility[];
  rescueTeams: RescueTeam[];
  hospitalRoute?: RouteResponse | null;
  shelterRoute?: RouteResponse | null;
  teamRoute?: RouteResponse | null;
  simulation?: FloodSimulationResult | null;
  selectedIds?: Set<string>;
  center: GeoPoint;
  onEntityClick?: (id: string) => void;
}

const markerIcon = (kind: "hospital" | "shelter" | "team", selected = false) => {
  const symbols = { hospital: "+", shelter: "⌂", team: "✦" } as const;
  const classes = { hospital: "medical", shelter: "shelter", team: "team" } as const;
  return divIcon({
    className: "tactical-marker-wrapper",
    html: `<span class="tactical-marker tactical-marker--${classes[kind]} ${selected ? "tactical-marker--selected" : ""}">${symbols[kind]}</span>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15],
  });
};

function point(value: GeoPoint): [number, number] { return [value.latitude, value.longitude]; }

function FitDistrict({ bounds }: { bounds: LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => { map.fitBounds(bounds, { padding: [34, 34] }); }, [map, bounds]);
  return null;
}

function ZoneMarker({ zone, affected, selected, onClick }: { zone: FloodZone; affected: boolean; selected: boolean; onClick?: (id: string) => void }) {
  const severityLabel = affected ? "Flood-affected" : "Operational";
  return <>
    <Circle center={point(zone.center)} radius={affected ? 1050 : 820} pathOptions={{ color: selected ? "#22c7ff" : affected ? "#ff3b3b" : "#169bd2", fillColor: affected ? "#ef3333" : "#0b86bf", fillOpacity: affected ? 0.16 : 0.045, weight: selected ? 3 : 2, dashArray: "7 7" }} />
    <CircleMarker center={point(zone.center)} radius={selected ? 18 : affected ? 14 : 10} pathOptions={{ color: selected ? "#ffffff" : affected ? "#ff3b3b" : "#22c7ff", fillColor: affected ? "#ff3b3b" : "#159fd1", fillOpacity: affected ? 0.95 : 0.75, weight: selected ? 4 : 2 }} eventHandlers={{ click: () => onClick?.(zone.id) }}>
      <Tooltip direction="top" offset={[0, -8]} permanent className="tactical-zone-label">{zone.name}</Tooltip>
      <Popup><strong>{zone.name}</strong><br />Status: {severityLabel}<br />Elevation: {zone.elevation_m} m<br />Population: {zone.population.toLocaleString()}</Popup>
    </CircleMarker>
  </>;
}

function FacilityMarker({ facility, selected, kind, onClick }: { facility: Facility; selected: boolean; kind: "hospital" | "shelter"; onClick?: (id: string) => void }) {
  return <Marker position={point(facility.location)} icon={markerIcon(kind, selected)} eventHandlers={{ click: () => onClick?.(facility.id) }}><Popup><strong>{facility.name}</strong><br />{kind === "hospital" ? "Hospital" : "Shelter"}<br />Capacity: {facility.capacity}<br />Occupancy: {facility.current_occupancy}</Popup></Marker>;
}

function TeamMarker({ team, selected, onClick }: { team: RescueTeam; selected: boolean; onClick?: (id: string) => void }) {
  return <Marker position={point(team.location)} icon={markerIcon("team", selected)} eventHandlers={{ click: () => onClick?.(team.id) }}><Popup><strong>{team.name}</strong><br />Status: {team.status}<br />Personnel: {team.personnel_count}</Popup></Marker>;
}

function RouteLine({ route, color, label }: { route?: RouteResponse | null; color: string; label: string }) {
  if (route?.status !== "success" || route.path.length < 2) return null;
  return <Polyline positions={route.path.map(point)} pathOptions={{ color, weight: 5, opacity: 0.92, lineCap: "round" }}><Popup>{label} route · {route.distance_km} km</Popup></Polyline>;
}

export function OperationalMap({ zones, hospitals, shelters, rescueTeams, hospitalRoute, shelterRoute, teamRoute, simulation, selectedIds, center, onEntityClick }: OperationalMapProps) {
  const allPoints = useMemo(
    () => [...zones.map((z) => point(z.center)), ...hospitals.map((h) => point(h.location)), ...shelters.map((s) => point(s.location)), ...rescueTeams.map((t) => point(t.location))],
    [zones, hospitals, shelters, rescueTeams],
  );
  const bounds: LatLngBoundsExpression = allPoints.length ? allPoints : [point(center), point(center)];
  const affectedIds = useMemo(
    () => new Set(simulation?.affected_zones.map((z) => z.zone_id) ?? []),
    [simulation?.affected_zones],
  );
  const zoneById = useMemo(() => new Map(zones.map((z) => [z.id, z])), [zones]);
    return <section className="relative overflow-hidden rounded-2xl border border-[#183650] bg-[#071522] shadow-panel">

    <div className="relative">
      <MapContainer center={point(center)} zoom={13} scrollWheelZoom className="h-[660px] w-full">
        <TileLayer attribution='&copy; OpenStreetMap contributors &copy; CARTO' url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" subdomains="abcd" />
        <FitDistrict bounds={bounds} />
        {zones.map((zone) => <ZoneMarker key={zone.id} zone={zone} affected={affectedIds.has(zone.id)} selected={selectedIds?.has(zone.id) ?? false} onClick={onEntityClick} />)}
        {hospitals.map((facility) => <FacilityMarker key={facility.id} facility={facility} kind="hospital" selected={selectedIds?.has(facility.id) ?? false} onClick={onEntityClick} />)}
        {shelters.map((facility) => <FacilityMarker key={facility.id} facility={facility} kind="shelter" selected={selectedIds?.has(facility.id) ?? false} onClick={onEntityClick} />)}
        {rescueTeams.map((team) => <TeamMarker key={team.id} team={team} selected={selectedIds?.has(team.id) ?? false} onClick={onEntityClick} />)}
        {simulation?.blocked_roads.map((road) => { const from = zoneById.get(road.from_zone_id); const to = zoneById.get(road.to_zone_id); if (!from || !to) return null; return <Polyline key={road.road_id} positions={[point(from.center), point(to.center)]} pathOptions={{ color: "#ff4d4d", weight: 6, opacity: 0.95, dashArray: "12 8" }}><Popup><strong>Blocked road: {road.road_name}</strong><br />{road.reason}</Popup></Polyline>; })}
        <RouteLine route={hospitalRoute} color="#ff5964" label="Hospital" />
        <RouteLine route={shelterRoute} color="#ffc233" label="Shelter" />
        <RouteLine route={teamRoute} color="#22d3a7" label="Rescue team" />
      </MapContainer>
      <div className="absolute bottom-4 left-4 right-4 z-[1000] flex flex-wrap gap-x-4 gap-y-2 rounded-xl border border-[#1a435f] bg-[#07111f]/94 px-4 py-3 text-[11px] text-slate-100 shadow-2xl backdrop-blur"><span><b className="mr-1.5 text-sky-400">●</b>Operational zone</span><span><b className="mr-1.5 text-rose-400">●</b>Flood-affected</span><span><b className="mr-1.5 text-rose-400">●</b>Hospital</span><span><b className="mr-1.5 text-amber-300">●</b>Shelter</span><span><b className="mr-1.5 text-emerald-400">●</b>Rescue team</span><span><b className="mr-1.5 text-red-500">━━</b>Blocked road</span><span><b className="mr-1.5 text-emerald-400">━━</b>Safe route</span></div>
    </div>
  </section>;
}
