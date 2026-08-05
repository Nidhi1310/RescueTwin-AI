import type { Facility, FloodZone, GeoPoint, RescueTeam } from "../types";

interface OperationalMapProps {
  zones: FloodZone[];
  hospitals: Facility[];
  shelters: Facility[];
  rescueTeams: RescueTeam[];
}

interface Bounds {
  minLatitude: number;
  maxLatitude: number;
  minLongitude: number;
  maxLongitude: number;
}

function boundsFor(points: GeoPoint[]): Bounds {
  return {
    minLatitude: Math.min(...points.map((point) => point.latitude)),
    maxLatitude: Math.max(...points.map((point) => point.latitude)),
    minLongitude: Math.min(...points.map((point) => point.longitude)),
    maxLongitude: Math.max(...points.map((point) => point.longitude)),
  };
}

function positionFor(point: GeoPoint, bounds: Bounds): { left: string; top: string } {
  const horizontal = (point.longitude - bounds.minLongitude) / (bounds.maxLongitude - bounds.minLongitude);
  const vertical = (bounds.maxLatitude - point.latitude) / (bounds.maxLatitude - bounds.minLatitude);
  return { left: `${10 + horizontal * 80}%`, top: `${9 + vertical * 82}%` };
}

function Marker({ symbol, label, point, bounds, className }: { symbol: string; label: string; point: GeoPoint; bounds: Bounds; className: string }) {
  return (
    <div className="absolute -translate-x-1/2 -translate-y-1/2 group" style={positionFor(point, bounds)}>
      <div className={`grid h-7 w-7 place-items-center rounded-full border-2 border-ink text-xs font-black shadow-lg ${className}`}>{symbol}</div>
      <div className="pointer-events-none absolute left-1/2 top-8 z-20 hidden w-max max-w-44 -translate-x-1/2 rounded bg-ink px-2 py-1 text-[10px] font-medium text-slate-100 shadow-xl group-hover:block">{label}</div>
    </div>
  );
}

export function OperationalMap({ zones, hospitals, shelters, rescueTeams }: OperationalMapProps) {
  const allPoints = [...zones.map((zone) => zone.center), ...hospitals.map((facility) => facility.location), ...shelters.map((facility) => facility.location), ...rescueTeams.map((team) => team.location)];
  const bounds = boundsFor(allPoints);

  return (
    <section className="relative min-h-[520px] overflow-hidden rounded-2xl border border-line bg-[#0d1b2a] shadow-panel">
      <div className="absolute inset-0 opacity-40 map-grid" />
      <div className="absolute -left-20 top-1/3 h-64 w-[110%] rotate-[-14deg] rounded-[100%] border-y border-water/20 bg-water/5" />
      <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-ink/60 to-transparent" />
      <div className="relative z-10 flex items-start justify-between p-5">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water">District overview</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Operational map shell</h2>
        </div>
        <div className="rounded-lg border border-white/10 bg-ink/70 px-3 py-2 text-xs text-slate-300">Static district data</div>
      </div>
      <div className="absolute inset-0 pt-16">
        {zones.map((zone) => (
          <div key={zone.id} className="absolute -translate-x-1/2 -translate-y-1/2" style={positionFor(zone.center, bounds)}>
            <div className="grid h-14 w-14 place-items-center rounded-full border border-water/50 bg-water/15 text-center text-[10px] font-semibold leading-tight text-sky-100 shadow-lg backdrop-blur-sm">
              {zone.name}
            </div>
          </div>
        ))}
        {hospitals.map((facility) => <Marker key={facility.id} symbol="+" label={facility.name} point={facility.location} bounds={bounds} className="bg-rose-400 text-rose-950" />)}
        {shelters.map((facility) => <Marker key={facility.id} symbol="⌂" label={facility.name} point={facility.location} bounds={bounds} className="bg-amber-300 text-amber-950" />)}
        {rescueTeams.map((team) => <Marker key={team.id} symbol="◆" label={`${team.name} · ${team.status}`} point={team.location} bounds={bounds} className="bg-rescue text-emerald-950" />)}
      </div>
      <div className="absolute bottom-5 left-5 z-10 flex flex-wrap gap-3 rounded-lg border border-white/10 bg-ink/75 px-3 py-2 text-xs text-slate-200 backdrop-blur">
        <span><b className="mr-1 text-water">●</b>Zone</span>
        <span><b className="mr-1 text-rose-400">●</b>Hospital</span>
        <span><b className="mr-1 text-amber-300">●</b>Shelter</span>
        <span><b className="mr-1 text-rescue">●</b>Rescue team</span>
      </div>
    </section>
  );
}
