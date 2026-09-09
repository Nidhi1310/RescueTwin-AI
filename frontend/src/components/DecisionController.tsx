import { useEffect, useState } from "react";
import { fetchDecisionBundle, fetchSimulation, fetchReport } from "../api";
import type { DistrictProfile, RainfallScenario, FloodSimulationResult, DecisionEngineResponse, IncidentReportResponse } from "../types";
import { OperationalMap } from "./OperationalMap";

interface DecisionControllerProps {
  district: DistrictProfile;
}

const scenarios: RainfallScenario[] = ["moderate", "severe", "extreme"];

export function DecisionController({ district }: DecisionControllerProps) {
  const [incidentZoneId, setIncidentZoneId] = useState<string | null>(null);
  const [decision, setDecision] = useState<DecisionEngineResponse | null>(null);
  const [report, setReport] = useState<IncidentReportResponse | null>(null);
  
  const [scenario, setScenario] = useState<RainfallScenario>("moderate");
  const [simulation, setSimulation] = useState<FloodSimulationResult | null>(null);
  const [loadingSimulation, setLoadingSimulation] = useState(true);
  const [loadingDecision, setLoadingDecision] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);

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
    return () => { cancelled = true; };
  }, [scenario]);

  useEffect(() => {
    if (!incidentZoneId) {
      setDecision(null);
      setReport(null);
      return;
    }
    
    // Find zone to extract realistic data
    const zone = district.zones.find(z => z.id === incidentZoneId);
    if (!zone) return;
    
    let cancelled = false;
    setLoadingDecision(true);
    setReport(null);
    
    fetchDecisionBundle(zone.id, scenario, zone.elevation_m, zone.drainage_score)
      .then((result) => {
        if (!cancelled) setDecision(result);
      })
      .catch((error) => {
        console.error(error);
        if (!cancelled) setDecision(null);
      })
      .finally(() => {
        if (!cancelled) setLoadingDecision(false);
      });
      
    return () => { cancelled = true; };
  }, [incidentZoneId, scenario, district.zones]);

  const handleEntityClick = (id: string) => {
    // Only allow selecting zones as incidents
    const isZone = district.zones.some(z => z.id === id);
    if (isZone) {
      setIncidentZoneId(id);
    }
  };

  const generateReport = () => {
    if (!decision) return;
    setLoadingReport(true);
    fetchReport(decision)
      .then(setReport)
      .catch(console.error)
      .finally(() => setLoadingReport(false));
  };

  // Build a set of selected IDs to highlight in the map
  const selectedIds = new Set<string>();
  if (incidentZoneId) selectedIds.add(incidentZoneId);
  if (decision) {
    selectedIds.add(decision.hospital_recommendation.recommended_hospital_id);
    selectedIds.add(decision.shelter_recommendation.recommended_shelter_id);
    selectedIds.add(decision.team_allocation.assigned_team_id);
  }

  return (
    <div className="relative">
      <OperationalMap
        zones={district.zones}
        hospitals={district.hospitals}
        shelters={district.shelters}
        rescueTeams={district.rescue_teams}
        hospitalRoute={decision?.hospital_route}
        shelterRoute={decision?.shelter_route}
        teamRoute={decision?.team_route}
        simulation={simulation}
        center={district.metadata.center}
        selectedIds={selectedIds}
        onEntityClick={handleEntityClick}
      />

      {/* Scenario Selector Panel */}
      <div className="absolute left-5 top-5 z-[1000] w-64 rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur">
        <div className="mb-2 flex items-center justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-water">Scenario</p>
            <h3 className="mt-1 text-sm font-semibold text-white">Rainfall simulation</h3>
          </div>
          {loadingSimulation && <span className="text-[10px] text-slate-400">Loading...</span>}
        </div>
        <div className="grid grid-cols-3 gap-1 rounded-lg bg-slate-900/80 p-1">
          {scenarios.map((value) => (
            <button
              key={value}
              type="button"
              onClick={() => setScenario(value)}
              className={`rounded-md px-2 py-2 text-[10px] font-bold uppercase transition ${
                scenario === value ? "bg-water text-slate-950" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              {value}
            </button>
          ))}
        </div>
        <p className="mt-3 text-[11px] text-slate-400">Click any <strong className="text-sky-400">zone</strong> on the map to run the decision engine for that location.</p>
      </div>

      {/* Recommendations Panel */}
      <div className="absolute right-5 top-5 z-[1000] w-[340px] max-h-[85vh] overflow-y-auto rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur scrollbar-hide">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-water">Decision Engine</h3>
          {incidentZoneId && (
            <button type="button" onClick={() => setIncidentZoneId(null)} className="text-[11px] font-semibold text-slate-400 hover:text-white">
              CLEAR
            </button>
          )}
        </div>
        
        {!incidentZoneId ? (
          <p className="text-sm text-slate-400">No incident selected. Click a flood zone to begin analysis.</p>
        ) : loadingDecision ? (
          <p className="animate-pulse text-sm text-slate-400">Analyzing incident parameters and calculating optimal routes...</p>
        ) : decision ? (
          <div className="space-y-4">
              {/* Prediction */}
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Flood Prediction
              </p>

              <div className="mt-1 flex items-end gap-2">
                <span className="text-2xl font-black text-white">
                  {decision.simulation.severity_score.toFixed(0)}
                  <span className="text-sm text-slate-500">/100</span>
                </span>

                <span className="mb-1 rounded bg-slate-900 px-2 py-0.5 text-[10px] font-semibold uppercase text-rose-400">
                  {decision.prediction.risk_level} RISK
                </span>
              </div>
            </div>

            {/* Rescue Team */}
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                Dispatched Rescue Team
              </p>

              <p className="mt-1 font-semibold text-white">
                {decision.team_allocation.selected_team.team_name}
              </p>

              <div className="mt-1 flex justify-between text-xs text-slate-400">
                <span>
                  {decision.team_allocation.selected_team.route_distance_km} km away
                </span>

                <span>
                  ETA: {decision.team_allocation.selected_team.estimated_travel_time_minutes} mins
                </span>
              </div>

              {!decision.team_route || decision.team_route.status !== "success" ? (
                <p className="mt-2 text-[10px] text-rose-400 uppercase font-bold">
                  NO SAFE ROUTE
                </p>
              ) : null}
            </div>

            {/* Hospital */}
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-rose-400">
                Recommended Hospital
              </p>

              <p className="mt-1 font-semibold text-white">
                {decision.hospital_recommendation.selected_hospital?.hospital_name ??
                  "No suitable hospital"}
              </p>

              <div className="mt-1 flex justify-between text-xs text-slate-400">
                <span>
                  {decision.hospital_recommendation.selected_hospital?.route_distance_km ??
                    "N/A"}{" "}
                  km away
                </span>

                <span>
                  {decision.hospital_recommendation.selected_hospital?.available_capacity ??
                    "N/A"}{" "}
                  beds
                </span>
              </div>
            </div>

            {/* Shelter */}
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
              <p className="text-[10px] font-bold uppercase tracking-wider text-amber-400">
                Evacuation Shelter
              </p>

              <p className="mt-1 font-semibold text-white">
                {decision.shelter_recommendation.selected_shelter?.shelter_name ??
                  "No suitable shelter"}
              </p>

              <div className="mt-1 flex justify-between text-xs text-slate-400">
                <span>
                  {decision.shelter_recommendation.selected_shelter?.route_distance_km ??
                    "N/A"}{" "}
                  km away
                </span>

                <span>
                  {decision.shelter_recommendation.selected_shelter?.available_capacity ??
                    "N/A"}{" "}
                  spaces
                </span>
              </div>
            </div>
            {/* Report Button */}
            {!report ? (
              <button 
                type="button" 
                onClick={generateReport}
                disabled={loadingReport}
                className="w-full rounded-lg bg-water py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:opacity-50"
              >
                {loadingReport ? "Generating..." : "Generate Incident Report"}
              </button>
            ) : (
              <div className="rounded-lg border border-water/30 bg-water/5 p-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-water">AI Incident Report</p>
                <div className="prose prose-invert prose-sm mt-2 max-w-none text-slate-300">
                  <pre className="whitespace-pre-wrap font-sans text-xs">{report.report_content}</pre>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
