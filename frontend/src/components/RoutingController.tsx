import { useEffect, useState } from "react";
import { fetchRoute } from "../api";
import type { DistrictProfile, RouteResponse } from "../types";
import { OperationalMap } from "./OperationalMap";

interface RoutingControllerProps {
  district: DistrictProfile;
}

export function RoutingController({ district }: RoutingControllerProps) {
  const [startId, setStartId] = useState<string | null>(null);
  const [endId, setEndId] = useState<string | null>(null);
  const [route, setRoute] = useState<RouteResponse | null>(null);
  const scenario = "moderate"; // Default scenario for now until UI switcher is added

  useEffect(() => {
    if (startId && endId) {
      fetchRoute(startId, endId, scenario).then(setRoute).catch(console.error);
    } else {
      setRoute(null);
    }
  }, [startId, endId, scenario]);

  const handleEntityClick = (id: string) => {
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
  };

  return (
    <div className="relative">
      <OperationalMap 
        zones={district.zones}
        hospitals={district.hospitals}
        shelters={district.shelters}
        rescueTeams={district.rescue_teams}
        route={route} 
        startId={startId}
        endId={endId}
        onEntityClick={handleEntityClick} 
      />
      
      {(startId || endId) && (
        <div className="absolute top-5 right-5 z-[500] w-72 rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur">
          <div className="mb-3 flex items-center justify-between">
             <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-water">Safe Routing</h3>
             <button type="button" onClick={resetRouting} className="text-[11px] font-semibold text-slate-400 hover:text-white transition">CLEAR</button>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
              <span className="text-slate-300">Start:</span>
              <span className="truncate font-medium text-white">{startId || "Select point on map"}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-400"></span>
              <span className="text-slate-300">End:</span>
              <span className="truncate font-medium text-white">{endId || "Select point on map"}</span>
            </div>
          </div>

          {route && (
            <div className="mt-4 border-t border-slate-700 pt-3">
              {route.status === "success" ? (
                <div>
                  <p className="text-sm font-semibold text-emerald-400">Safe route found</p>
                  <p className="mt-1 text-xs text-slate-300">Distance: {route.distance_km} km</p>
                </div>
              ) : (
                <p className="text-sm font-semibold text-rose-400">No safe route available</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
