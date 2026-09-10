import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
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

function point(value: GeoPoint): [number, number] {
  return [value.latitude, value.longitude];
}

function FitDistrict({ bounds }: { bounds: LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(bounds, { padding: [34, 34] });
  }, [map, bounds]);
  return null;
}

function ZoneMarker({ zone, affected, selected, onClick }: { zone: FloodZone; affected: boolean; selected: boolean; onClick?: (id: string) => void }) {
  const severityLabel = affected ? "Flood-affected" : "Operational";
  return (
    <CircleMarker
      center={point(zone.center)}
      radius={selected ? 17 : affected ? 14 : 11}
      pathOptions={{
        color: selected ? "#ffffff" : affected ? "#f43f5e" : "#38bdf8",
        fillColor: affected ? "#f43f5e" : "#0ea5e9",
        fillOpacity: affected ? 0.48 : 0.24,
        weight: selected ? 4 : 2,
      }}
      eventHandlers={{ click: () => onClick?.(zone.id) }}
    >
      <Popup>
        <strong>{zone.name}</strong>
        <br />Status: {severityLabel}
        <br />Elevation: {zone.elevation_m} m
        <br />Population: {zone.population.toLocaleString()}
      </Popup>
    </CircleMarker>
  );
}

function FacilityMarker({ facility, selected, kind, onClick }: { facility: Facility; selected: boolean; kind: "hospital" | "shelter"; onClick?: (id: string) => void }) {
  const fillColor = kind === "hospital" ? "#fb7185" : "#fbbf24";
  const label = kind === "hospital" ? "Hospital" : "Shelter";
  return (
    <CircleMarker
      center={point(facility.location)}
      radius={selected ? 12 : 8}
      pathOptions={{ color: "#0f172a", fillColor, fillOpacity: 0.96, weight: selected ? 4 : 2 }}
      eventHandlers={{ click: () => onClick?.(facility.id) }}
    >
      <Popup>
        <strong>{facility.name}</strong>
        <br />{label}
        <br />Capacity: {facility.capacity}
        <br />Occupancy: {facility.current_occupancy}
      </Popup>
    </CircleMarker>
  );
}

function TeamMarker({ team, selected, onClick }: { team: RescueTeam; selected: boolean; onClick?: (id: string) => void }) {
  const available = team.status === "available";
  return (
    <CircleMarker
      center={point(team.location)}
      radius={selected ? 11 : 7}
      pathOptions={{ color: "#064e3b", fillColor: available ? "#34d399" : "#94a3b8", fillOpacity: 0.96, weight: selected ? 4 : 2 }}
      eventHandlers={{ click: () => onClick?.(team.id) }}
    >
      <Popup>
        <strong>{team.name}</strong>
        <br />Status: {team.status}
        <br />Personnel: {team.personnel_count}
      </Popup>
    </CircleMarker>
  );
}

function RouteLine({ route, color, label }: { route?: RouteResponse | null; color: string; label: string }) {
  if (route?.status !== "success" || route.path.length < 2) return null;
  return (
    <Polyline positions={route.path.map(point)} pathOptions={{ color, weight: 6, opacity: 0.9 }}>
      <Popup>{label} route · {route.distance_km} km</Popup>
    </Polyline>
  );
}

export function OperationalMap({ zones, hospitals, shelters, rescueTeams, hospitalRoute, shelterRoute, teamRoute, simulation, selectedIds = new Set(), center, onEntityClick }: OperationalMapProps) {
  const allPoints = [
    ...zones.map((z) => point(z.center)),
    ...hospitals.map((h) => point(h.location)),
    ...shelters.map((s) => point(s.location)),
    ...rescueTeams.map((t) => point(t.location)),
  ];
  const bounds: LatLngBoundsExpression = allPoints.length ? allPoints : [point(center), point(center)];
  const affectedIds = new Set(simulation?.affected_zones.map((z) => z.zone_id) ?? []);
  const zoneById = new Map(zones.map((z) => [z.id, z]));
  const scenarioLabel = simulation?.scenario ? simulation.scenario.toUpperCase() : "NO SCENARIO";
  const affectedCount = simulation?.affected_zones.length ?? 0;
  const blockedCount = simulation?.blocked_roads.length ?? 0;

  return (
    <section className="relative overflow-hidden rounded-2xl border border-line bg-[#0d1b2a] shadow-panel">
      <div className="relative z-20 flex flex-wrap items-center justify-between gap-4 border-b border-white/10 bg-[#0d1b2a]/95 p-4 backdrop-blur">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water">Live tactical map</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Flood response operations</h2>
          <p className="mt-1 text-xs text-slate-400">Click a map entity to inspect operational details.</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold">
          <span className="rounded-full border border-water/30 bg-water/10 px-3 py-1.5 text-water">{scenarioLabel}</span>
          <span className="rounded-full border border-rose-400/30 bg-rose-400/10 px-3 py-1.5 text-rose-200">{affectedCount} affected zones</span>
          <span className="rounded-full border border-red-400/30 bg-red-400/10 px-3 py-1.5 text-red-200">{blockedCount} blocked roads</span>
        </div>
      </div>

      <div className="relative">
        <MapContainer center={point(center)} zoom={13} scrollWheelZoom className="h-[560px] w-full">
          <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <FitDistrict bounds={bounds} />

          {zones.map((zone) => <ZoneMarker key={zone.id} zone={zone} affected={affectedIds.has(zone.id)} selected={selectedIds.has(zone.id)} onClick={onEntityClick} />)}
          {hospitals.map((facility) => <FacilityMarker key={facility.id} facility={facility} kind="hospital" selected={selectedIds.has(facility.id)} onClick={onEntityClick} />)}
          {shelters.map((facility) => <FacilityMarker key={facility.id} facility={facility} kind="shelter" selected={selectedIds.has(facility.id)} onClick={onEntityClick} />)}
          {rescueTeams.map((team) => <TeamMarker key={team.id} team={team} selected={selectedIds.has(team.id)} onClick={onEntityClick} />)}

          {simulation?.blocked_roads.map((road) => {
            const from = zoneById.get(road.from_zone_id);
            const to = zoneById.get(road.to_zone_id);
            if (!from || !to) return null;
            return (
              <Polyline key={road.road_id} positions={[point(from.center), point(to.center)]} pathOptions={{ color: "#ef4444", weight: 6, opacity: 0.95, dashArray: "12 8" }}>
                <Popup><strong>Blocked road: {road.road_name}</strong><br />{road.reason}</Popup>
              </Polyline>
            );
          })}

          <RouteLine route={hospitalRoute} color="#fb7185" label="Hospital" />
          <RouteLine route={shelterRoute} color="#fbbf24" label="Shelter" />
          <RouteLine route={teamRoute} color="#34d399" label="Rescue team" />
        </MapContainer>

        <div className="pointer-events-none absolute left-4 top-4 z-[1000] rounded-xl border border-white/15 bg-ink/90 px-3 py-2 text-[11px] text-slate-200 shadow-xl backdrop-blur">
          <div className="font-bold uppercase tracking-[0.12em] text-white">Operational overlays</div>
          <div className="mt-1 text-slate-400">Scenario-driven · live simulation state</div>
        </div>

        <div className="absolute bottom-4 left-4 right-4 z-[1000] flex flex-wrap gap-x-4 gap-y-2 rounded-xl border border-white/15 bg-ink/95 px-4 py-3 text-[11px] text-slate-100 shadow-xl backdrop-blur">
          <span><b className="mr-1.5 text-sky-400">●</b>Operational zone</span>
          <span><b className="mr-1.5 text-rose-400">●</b>Flood-affected</span>
          <span><b className="mr-1.5 text-rose-400">●</b>Hospital</span>
          <span><b className="mr-1.5 text-amber-300">●</b>Shelter</span>
          <span><b className="mr-1.5 text-emerald-400">●</b>Rescue team</span>
          <span><b className="mr-1.5 text-red-500">━━</b>Blocked road</span>
          <span><b className="mr-1.5 text-emerald-400">━━</b>Safe route</span>
        </div>
      </div>
    </section>
  );
}
