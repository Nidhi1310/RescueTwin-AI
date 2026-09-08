import { useEffect, useState } from "react";
import { fetchRoute, fetchSimulation } from "../api";
import type { DistrictProfile, RainfallScenario, RouteResponse, FloodSimulationResult } from "../types";
import { OperationalMap } from "./OperationalMap";

interface RoutingControllerProps {
  district: DistrictProfile;
  scenario: RainfallScenario;
  onScenarioChange: (scenario: RainfallScenario) => void;
  onIncidentZoneChange: (zoneId: string) => void;
}

const scenarios: RainfallScenario[] = ["moderate", "severe", "extreme"];

export function RoutingController({ district, scenario, onScenarioChange, onIncidentZoneChange }: RoutingControllerProps) {
  const [startId, setStartId] = useState<string | null>(null);
  const [endId, setEndId] = useState<string | null>(null);
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const [simulation, setSimulation] = useState<FloodSimulationResult | null>(null);
  const [loadingSimulation, setLoadingSimulation] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoadingSimulation(true);
    fetchSimulation(scenario)
      .then((result) => {
        if (!cancelled) setSimulation(result);
      })
      .catch(console.error)
      .finally(() => {
        if (!cancelled) setLoadingSimulation(false);
      });
    return () => {
      cancelled = true;
    };
  }, [scenario]);

  useEffect(() => {
    let cancelled = false;
    if (!startId || !endId) {
      setRoute(null);
      return;
    }
    fetchRoute(startId, endId, scenario)
      .then((result) => {
        if (!cancelled) setRoute(result);
      })
      .catch((error) => {
        console.error(error);
        if (!cancelled) setRoute(null);
      });
    return () => {
      cancelled = true;
    };
  }, [startId, endId, scenario]);

  const handleEntityClick = (id: string) => {
    if (id.startsWith("zone-")) onIncidentZoneChange(id);

    if (!startId) {
      setStartId(id);
    } else if (!endId && id !== startId) {
      setEndId(id);
    } else {
      setStartId(id);
      setEndId(null);
    }
  };

  const resetRouting = () => {
    setStartId(null);
    setEndId(null);
    setRoute(null);
  };

  return (
    <div className="relative">
      <OperationalMap
        zones={district.zones}
        hospitals={district.hospitals}
        shelters={district.shelters}
        rescueTeams={district.rescue_teams}
        route={route}
        simulation={simulation}
        center={district.metadata.center}
        startId={startId}
        endId={endId}
        onEntityClick={handleEntityClick}
      />

      <div className="absolute left-5 top-5 z-[1000] w-64 rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur">
        <div className="mb-2 flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-water">Scenario</p>
            <h3 className="mt-1 text-sm font-semibold text-white">Rainfall simulation</h3>
          </div>
          {loadingSimulation && <span className="text-[10px] text-slate-400">Loading…</span>}
        </div>
        <div className="grid grid-cols-3 gap-1 rounded-lg bg-slate-900/80 p-1">
          {scenarios.map((value) => (
            <button key={value} type="button" onClick={() => onScenarioChange(value)} className={`rounded-md px-2 py-2 text-[10px] font-bold uppercase transition ${scenario === value ? "bg-water text-slate-950" : "text-slate-300 hover:bg-slate-800"}`}>
              {value}
            </button>
          ))}
        </div>
        {simulation && (
          <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
            <div className="rounded-lg border border-white/10 bg-slate-900/60 p-2"><p className="text-slate-400">Severity</p><p className="mt-1 font-bold text-white">{simulation.severity_score.toFixed(1)}</p></div>
            <div className="rounded-lg border border-white/10 bg-slate-900/60 p-2"><p className="text-slate-400">Blocked</p><p className="mt-1 font-bold text-rose-400">{simulation.blocked_roads.length}</p></div>
          </div>
        )}
      </div>

      <div className="absolute right-5 top-5 z-[1000] w-72 rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur">
        <div className="mb-3 flex items-center justify-between"><h3 className="text-xs font-bold uppercase tracking-[0.18em] text-water">Safe Routing</h3>{(startId || endId) && <button type="button" onClick={resetRouting} className="text-[11px] font-semibold text-slate-400 hover:text-white">CLEAR</button>}</div>
        <p className="mb-3 text-[11px] text-slate-400">Click any zone, hospital, shelter, or rescue team twice to create a route.</p>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-400" /><span className="text-slate-300">Start:</span><span className="truncate font-medium text-white">{startId || "Select point"}</span></div>
          <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-blue-400" /><span className="text-slate-300">End:</span><span className="truncate font-medium text-white">{endId || "Select point"}</span></div>
        </div>
        {route && <div className="mt-4 border-t border-slate-700 pt-3">{route.status === "success" ? <div><p className="text-sm font-semibold text-emerald-400">Safe route found</p><p className="mt-1 text-xs text-slate-300">Distance: {route.distance_km} km</p></div> : <p className="text-sm font-semibold text-rose-400">No safe route available</p>}</div>}
      </div>
    </div>
  );
}
