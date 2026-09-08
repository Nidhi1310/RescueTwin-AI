import "leaflet/dist/leaflet.css";

import { CircleMarker, MapContainer, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";
import type { Facility, FloodSimulationResult, FloodZone, GeoPoint, RescueTeam, RouteResponse } from "../types";

interface OperationalMapProps {
  zones: FloodZone[];
  hospitals: Facility[];
  shelters: Facility[];
  rescueTeams: RescueTeam[];
  route?: RouteResponse | null;
  simulation?: FloodSimulationResult | null;
  startId?: string | null;
  endId?: string | null;
  center: GeoPoint;
  onEntityClick?: (id: string) => void;
}

function point(point: GeoPoint): [number, number] {
  return [point.latitude, point.longitude];
}

function FitDistrict({ bounds }: { bounds: LatLngBoundsExpression }) {
  const map = useMap();
  map.fitBounds(bounds, { padding: [28, 28] });
  return null;
}

function ZoneMarker({
  zone,
  affected,
  selected,
  onClick,
}: {
  zone: FloodZone;
  affected: boolean;
  selected: boolean;
  onClick?: (id: string) => void;
}) {
  return (
    <CircleMarker
      center={point(zone.center)}
      radius={selected ? 16 : 13}
      pathOptions={{
        color: selected ? "#ffffff" : affected ? "#ef4444" : "#38bdf8",
        fillColor: affected ? "#ef4444" : "#0ea5e9",
        fillOpacity: affected ? 0.42 : 0.2,
        weight: selected ? 4 : 2,
      }}
      eventHandlers={{ click: () => onClick?.(zone.id) }}
    >
      <Popup>
        <strong>{zone.name}</strong>
        <br />
        {affected ? "Flood-affected zone" : "Operational zone"}
      </Popup>
    </CircleMarker>
  );
}

function FacilityMarker({
  facility,
  selected,
  kind,
  onClick,
}: {
  facility: Facility;
  selected: boolean;
  kind: "hospital" | "shelter";
  onClick?: (id: string) => void;
}) {
  const fillColor = kind === "hospital" ? "#fb7185" : "#fbbf24";
  return (
    <CircleMarker
      center={point(facility.location)}
      radius={selected ? 11 : 8}
      pathOptions={{ color: "#0f172a", fillColor, fillOpacity: 0.95, weight: selected ? 4 : 2 }}
      eventHandlers={{ click: () => onClick?.(facility.id) }}
    >
      <Popup>
        <strong>{facility.name}</strong>
        <br />
        {kind === "hospital" ? "Hospital" : "Shelter"}
        <br />
        Capacity: {facility.capacity} · Occupancy: {facility.current_occupancy}
      </Popup>
    </CircleMarker>
  );
}

function TeamMarker({ team, selected, onClick }: { team: RescueTeam; selected: boolean; onClick?: (id: string) => void }) {
  return (
    <CircleMarker
      center={point(team.location)}
      radius={selected ? 10 : 7}
      pathOptions={{
        color: "#064e3b",
        fillColor: team.status === "available" ? "#34d399" : "#94a3b8",
        fillOpacity: 0.95,
        weight: selected ? 4 : 2,
      }}
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

export function OperationalMap({
  zones,
  hospitals,
  shelters,
  rescueTeams,
  route,
  simulation,
  startId,
  endId,
  center,
  onEntityClick,
}: OperationalMapProps) {
  const allPoints = [
    ...zones.map((z) => point(z.center)),
    ...hospitals.map((h) => point(h.location)),
    ...shelters.map((s) => point(s.location)),
    ...rescueTeams.map((t) => point(t.location)),
  ];
  const bounds: LatLngBoundsExpression = allPoints.length ? allPoints : [point(center), point(center)];
  const affectedIds = new Set(simulation?.affected_zones.map((z) => z.zone_id) ?? []);
  const zoneById = new Map(zones.map((z) => [z.id, z]));

  return (
    <section className="relative overflow-hidden rounded-2xl border border-line bg-[#0d1b2a] shadow-panel">
      <div className="relative z-20 flex items-start justify-between gap-4 p-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water">Live tactical map</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Flood response operations</h2>
        </div>
        <div className="rounded-lg border border-white/10 bg-ink/90 px-3 py-2 text-xs text-slate-200 shadow-lg">
          {simulation?.scenario.toUpperCase() ?? "NO SCENARIO"} · {simulation?.blocked_roads.length ?? 0} blocked roads
        </div>
      </div>

      <MapContainer center={point(center)} zoom={13} scrollWheelZoom className="h-[560px] w-full">
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitDistrict bounds={bounds} />

        {zones.map((zone) => (
          <ZoneMarker
            key={zone.id}
            zone={zone}
            affected={affectedIds.has(zone.id)}
            selected={startId === zone.id || endId === zone.id}
            onClick={onEntityClick}
          />
        ))}

        {hospitals.map((facility) => (
          <FacilityMarker key={facility.id} facility={facility} kind="hospital" selected={startId === facility.id || endId === facility.id} onClick={onEntityClick} />
        ))}
        {shelters.map((facility) => (
          <FacilityMarker key={facility.id} facility={facility} kind="shelter" selected={startId === facility.id || endId === facility.id} onClick={onEntityClick} />
        ))}
        {rescueTeams.map((team) => (
          <TeamMarker key={team.id} team={team} selected={startId === team.id || endId === team.id} onClick={onEntityClick} />
        ))}

        {simulation?.blocked_roads.map((road) => {
          const from = zoneById.get(road.from_zone_id);
          const to = zoneById.get(road.to_zone_id);
          if (!from || !to) return null;
          return (
            <Polyline
              key={road.road_id}
              positions={[point(from.center), point(to.center)]}
              pathOptions={{ color: "#ef4444", weight: 5, opacity: 0.9, dashArray: "10 8" }}
            >
              <Popup>
                <strong>Blocked road: {road.road_name}</strong>
                <br />{road.reason}
              </Popup>
            </Polyline>
          );
        })}

        {route?.status === "success" && route.path.length > 1 && (
          <Polyline
            positions={route.path.map(point)}
            pathOptions={{ color: "#22c55e", weight: 6, opacity: 0.9 }}
          >
            <Popup>Safe route · {route.distance_km} km</Popup>
          </Polyline>
        )}
      </MapContainer>

      <div className="absolute bottom-5 left-5 z-[1000] flex flex-wrap gap-3 rounded-lg border border-white/10 bg-ink/90 px-3 py-2 text-xs text-slate-100 shadow-xl">
        <span><b className="mr-1 text-sky-400">●</b>Zone</span>
        <span><b className="mr-1 text-rose-400">●</b>Hospital</span>
        <span><b className="mr-1 text-amber-300">●</b>Shelter</span>
        <span><b className="mr-1 text-emerald-400">●</b>Rescue team</span>
        <span><b className="mr-1 text-red-500">━</b>Blocked road</span>
        <span><b className="mr-1 text-green-400">━</b>Safe route</span>
      </div>
    </section>
  );
}
