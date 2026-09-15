import "leaflet/dist/leaflet.css";
import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Polygon, Polyline, Popup, TileLayer, Tooltip, useMap } from "react-leaflet";
import { divIcon } from "leaflet";
import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";
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
    iconSize: [34, 34],
    iconAnchor: [17, 17],
    popupAnchor: [0, -17],
  });
};

function point(value: GeoPoint): [number, number] {
  return [value.latitude, value.longitude];
}

function FitDistrict({ bounds }: { bounds: LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(bounds, { padding: [28, 28] });
  }, [map, bounds]);
  return null;
}

function LocateButton() {
  const map = useMap();
  const [locating, setLocating] = useState(false);

  const locate = () => {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        map.flyTo([coords.latitude, coords.longitude], Math.max(map.getZoom(), 14), { duration: 0.8 });
        setLocating(false);
      },
      () => setLocating(false),
      { enableHighAccuracy: true, timeout: 7000 },
    );
  };

  return (
    <button
      type="button"
      aria-label="Locate me"
      title="Locate me"
      onClick={locate}
      className="tactical-map-button"
    >
      <span className={locating ? "animate-pulse" : ""}>⌾</span>
    </button>
  );
}

function MapControls() {
  const map = useMap();
  const [layersOpen, setLayersOpen] = useState(false);

  return (
    <div className="absolute right-3 top-3 z-[1000] flex flex-col gap-1.5">
      <div className="tactical-map-control-group">
        <button type="button" aria-label="Zoom in" title="Zoom in" onClick={() => map.zoomIn()} className="tactical-map-button">+</button>
        <button type="button" aria-label="Zoom out" title="Zoom out" onClick={() => map.zoomOut()} className="tactical-map-button tactical-map-button--divider">−</button>
      </div>
      <button
        type="button"
        aria-label="Toggle map layers"
        title="Map layers"
        onClick={() => setLayersOpen((value) => !value)}
        className={`tactical-map-button ${layersOpen ? "tactical-map-button--active" : ""}`}
      >
        <span className="text-base">▱</span>
        <span className="text-[9px] font-semibold">Layers</span>
      </button>
      <LocateButton />
      {layersOpen && (
        <div className="absolute right-0 top-[112px] w-40 rounded-lg border border-[#1a435f] bg-[#07111f]/96 p-2.5 text-[10px] text-slate-300 shadow-2xl backdrop-blur-md">
          <p className="font-bold uppercase tracking-wider text-water">Map layers</p>
          <p className="mt-1.5 text-slate-400">Operational zones, flood impact, facilities, teams and routes are active.</p>
        </div>
      )}
    </div>
  );
}

function zonePolygon(zone: FloodZone, index: number, affected: boolean): LatLngExpression[] {
  const scale = affected ? 0.0105 : 0.0082;
  const shapes = [
    [[-0.85, -0.55], [-0.2, -1], [0.72, -0.78], [1, 0.02], [0.48, 0.85], [-0.38, 0.92], [-1, 0.35]],
    [[-0.9, -0.2], [-0.48, -0.92], [0.28, -1], [0.96, -0.35], [0.72, 0.58], [0.05, 0.95], [-0.72, 0.7]],
    [[-0.78, -0.72], [0.15, -1], [0.92, -0.45], [0.82, 0.48], [0.18, 1], [-0.72, 0.72], [-1, -0.05]],
  ] as const;
  const shape = shapes[index % shapes.length];
  return shape.map(([latOffset, lngOffset]) => [
    zone.center.latitude + latOffset * scale,
    zone.center.longitude + lngOffset * scale,
  ]);
}

function ZoneOverlay({
  zone,
  affected,
  selected,
  index,
  onClick,
}: {
  zone: FloodZone;
  affected: boolean;
  selected: boolean;
  index: number;
  onClick?: (id: string) => void;
}) {
  const severityLabel = affected ? "Flood-affected" : "Operational";
  const polygon = zonePolygon(zone, index, affected);

  return (
    <>
      <Polygon
        positions={polygon}
        pathOptions={{
          color: selected ? "#ffffff" : affected ? "#ff3038" : "#16a9ff",
          fillColor: affected ? "#ff2f38" : "#0a8fce",
          fillOpacity: affected ? 0.24 : 0.055,
          weight: selected ? 3 : 2,
          dashArray: "7 7",
          lineJoin: "round",
        }}
        eventHandlers={{ click: () => onClick?.(zone.id) }}
      />
      <Marker position={point(zone.center)} icon={divIcon({
        className: "zone-center-hitbox",
        html: "<span></span>",
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      })} eventHandlers={{ click: () => onClick?.(zone.id) }}>
        <Tooltip direction="top" offset={[0, -12]} permanent className="tactical-zone-label">
          {zone.name}
        </Tooltip>
        <Popup>
          <strong>{zone.name}</strong><br />
          Status: {severityLabel}<br />
          Elevation: {zone.elevation_m} m<br />
          Population: {zone.population.toLocaleString()}
        </Popup>
      </Marker>
    </>
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
  return (
    <Marker
      position={point(facility.location)}
      icon={markerIcon(kind, selected)}
      eventHandlers={{ click: () => onClick?.(facility.id) }}
    >
      <Popup>
        <strong>{facility.name}</strong><br />
        {kind === "hospital" ? "Hospital" : "Shelter"}<br />
        Capacity: {facility.capacity}<br />
        Occupancy: {facility.current_occupancy}
      </Popup>
    </Marker>
  );
}

function TeamMarker({ team, selected, onClick }: { team: RescueTeam; selected: boolean; onClick?: (id: string) => void }) {
  return (
    <Marker
      position={point(team.location)}
      icon={markerIcon("team", selected)}
      eventHandlers={{ click: () => onClick?.(team.id) }}
    >
      <Popup>
        <strong>{team.name}</strong><br />
        Status: {team.status}<br />
        Personnel: {team.personnel_count}
      </Popup>
    </Marker>
  );
}

function RouteLine({ route, color, label }: { route?: RouteResponse | null; color: string; label: string }) {
  if (route?.status !== "success" || route.path.length < 2) return null;
  return (
    <Polyline
      positions={route.path.map(point)}
      pathOptions={{ color, weight: 5, opacity: 0.95, lineCap: "round", lineJoin: "round" }}
    >
      <Popup>{label} route · {route.distance_km} km</Popup>
    </Polyline>
  );
}

export function OperationalMap({
  zones,
  hospitals,
  shelters,
  rescueTeams,
  hospitalRoute,
  shelterRoute,
  teamRoute,
  simulation,
  selectedIds,
  center,
  onEntityClick,
}: OperationalMapProps) {
  const allPoints = useMemo(
    () => [
      ...zones.map((z) => point(z.center)),
      ...hospitals.map((h) => point(h.location)),
      ...shelters.map((s) => point(s.location)),
      ...rescueTeams.map((t) => point(t.location)),
    ],
    [zones, hospitals, shelters, rescueTeams],
  );

  const bounds: LatLngBoundsExpression = allPoints.length ? allPoints : [point(center), point(center)];
  const affectedIds = useMemo(
    () => new Set(simulation?.affected_zones.map((z) => z.zone_id) ?? []),
    [simulation?.affected_zones],
  );
  const zoneById = useMemo(() => new Map(zones.map((z) => [z.id, z])), [zones]);

  return (
    <section className="relative overflow-hidden rounded-xl border border-[#16415f] bg-[#06111d] shadow-[0_18px_55px_rgba(0,0,0,.3)]">
      <div className="relative">
        <MapContainer center={point(center)} zoom={13} scrollWheelZoom className="h-[650px] w-full">
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FitDistrict bounds={bounds} />
          <MapControls />

          {zones.map((zone, index) => (
            <ZoneOverlay
              key={zone.id}
              zone={zone}
              index={index}
              affected={affectedIds.has(zone.id)}
              selected={selectedIds?.has(zone.id) ?? false}
              onClick={onEntityClick}
            />
          ))}

          {hospitals.map((facility) => (
            <FacilityMarker
              key={facility.id}
              facility={facility}
              kind="hospital"
              selected={selectedIds?.has(facility.id) ?? false}
              onClick={onEntityClick}
            />
          ))}

          {shelters.map((facility) => (
            <FacilityMarker
              key={facility.id}
              facility={facility}
              kind="shelter"
              selected={selectedIds?.has(facility.id) ?? false}
              onClick={onEntityClick}
            />
          ))}

          {rescueTeams.map((team) => (
            <TeamMarker
              key={team.id}
              team={team}
              selected={selectedIds?.has(team.id) ?? false}
              onClick={onEntityClick}
            />
          ))}

          {simulation?.blocked_roads.map((road) => {
            const from = zoneById.get(road.from_zone_id);
            const to = zoneById.get(road.to_zone_id);
            if (!from || !to) return null;
            return (
              <Polyline
                key={road.road_id}
                positions={[point(from.center), point(to.center)]}
                pathOptions={{
                  color: "#ff3b45",
                  weight: 5,
                  opacity: 0.96,
                  dashArray: "11 8",
                  lineCap: "round",
                }}
              >
                <Popup>
                  <strong>Blocked road: {road.road_name}</strong><br />
                  {road.reason}
                </Popup>
              </Polyline>
            );
          })}

          <RouteLine route={hospitalRoute} color="#ff5964" label="Hospital" />
          <RouteLine route={shelterRoute} color="#ffc233" label="Shelter" />
          <RouteLine route={teamRoute} color="#18e4d1" label="Rescue team" />
        </MapContainer>

        <div className="absolute bottom-3 left-3 right-3 z-[1000] flex flex-wrap items-center gap-x-5 gap-y-2 rounded-lg border border-[#16415f] bg-[#06111d]/94 px-4 py-3 text-[11px] text-slate-100 shadow-2xl backdrop-blur-md">
          <span className="flex items-center gap-2"><i className="legend-icon legend-icon--zone" />Operational zone</span>
          <span className="flex items-center gap-2"><i className="legend-icon legend-icon--flood" />Flood-affected</span>
          <span className="flex items-center gap-2"><i className="legend-icon legend-icon--hospital">+</i>Hospital</span>
          <span className="flex items-center gap-2"><i className="legend-icon legend-icon--shelter">⌂</i>Shelter</span>
          <span className="flex items-center gap-2"><i className="legend-icon legend-icon--team">✦</i>Rescue team</span>
          <span className="flex items-center gap-2"><i className="legend-line legend-line--blocked" />Blocked road</span>
          <span className="flex items-center gap-2"><i className="legend-line legend-line--safe" />Safe route</span>
        </div>
      </div>
    </section>
  );
}
