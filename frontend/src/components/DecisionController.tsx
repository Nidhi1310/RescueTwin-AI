import { useEffect, useState } from "react";
import { fetchDecisionBundle, fetchSimulation, fetchReport } from "../api";
import type { DistrictProfile, RainfallScenario, FloodSimulationResult, DecisionEngineResponse, IncidentReportResponse, ReasoningFactor } from "../types";
import { OperationalMap } from "./OperationalMap";
import { AnalyticsDashboard } from "./AnalyticsDashboard";

interface DecisionControllerProps { district: DistrictProfile; }
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
  const [decisionError, setDecisionError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingSimulation(true);
    fetchSimulation(scenario).then((result) => { if (!cancelled) setSimulation(result); })
      .catch((error) => { console.error(error); if (!cancelled) setSimulation(null); })
      .finally(() => { if (!cancelled) setLoadingSimulation(false); });
    return () => { cancelled = true; };
  }, [scenario]);

  useEffect(() => {
    if (!incidentZoneId) { setDecision(null); setReport(null); setDecisionError(null); return; }
    const zone = district.zones.find((z) => z.id === incidentZoneId);
    if (!zone) return;
    let cancelled = false;
    setLoadingDecision(true); setReport(null); setDecisionError(null);
    fetchDecisionBundle(zone.id, scenario, zone.elevation_m, zone.drainage_score)
      .then((result) => { if (!cancelled) setDecision(result); })
      .catch((error) => { console.error(error); if (!cancelled) { setDecision(null); setDecisionError("Unable to calculate the decision bundle. Please try again."); } })
      .finally(() => { if (!cancelled) setLoadingDecision(false); });
    return () => { cancelled = true; };
  }, [incidentZoneId, scenario, district.zones]);

  const handleEntityClick = (id: string) => { if (district.zones.some((z) => z.id === id)) setIncidentZoneId(id); };
  const generateReport = () => {
    if (!decision) return;
    setLoadingReport(true);
    fetchReport(decision).then(setReport).catch((error) => { console.error(error); }).finally(() => setLoadingReport(false));
  };

  const selectedIds = new Set<string>();
  if (incidentZoneId) selectedIds.add(incidentZoneId);
  if (decision?.hospital_recommendation.selected_hospital) selectedIds.add(decision.hospital_recommendation.selected_hospital.hospital_id);
  if (decision?.shelter_recommendation.selected_shelter) selectedIds.add(decision.shelter_recommendation.selected_shelter.shelter_id);
  if (decision?.team_allocation.selected_team) selectedIds.add(decision.team_allocation.selected_team.team_id);

  return (
    <div className="relative">
      <OperationalMap zones={district.zones} hospitals={district.hospitals} shelters={district.shelters} rescueTeams={district.rescue_teams}
        hospitalRoute={decision?.hospital_route} shelterRoute={decision?.shelter_route} teamRoute={decision?.team_route}
        simulation={simulation} center={district.metadata.center} selectedIds={selectedIds} onEntityClick={handleEntityClick} />

      <div className="absolute left-5 top-5 z-[1000] w-64 rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur">
        <div className="mb-2 flex items-center justify-between"><div><p className="text-[10px] font-bold uppercase tracking-[0.18em] text-water">Scenario</p><h3 className="mt-1 text-sm font-semibold text-white">Rainfall simulation</h3></div>{loadingSimulation && <span className="text-[10px] text-slate-400">Loading...</span>}</div>
        <div className="grid grid-cols-3 gap-1 rounded-lg bg-slate-900/80 p-1">{scenarios.map((value) => <button key={value} type="button" onClick={() => setScenario(value)} className={`rounded-md px-2 py-2 text-[10px] font-bold uppercase transition ${scenario === value ? "bg-water text-slate-950" : "text-slate-300 hover:bg-slate-800"}`}>{value}</button>)}</div>
        <p className="mt-3 text-[11px] text-slate-400">Click any <strong className="text-sky-400">zone</strong> on the map to run the decision engine for that location.</p>
      </div>

      <div className="absolute right-5 top-5 z-[1000] w-[340px] max-h-[85vh] overflow-y-auto rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur scrollbar-hide">
        <div className="mb-3 flex items-center justify-between"><h3 className="text-xs font-bold uppercase tracking-[0.18em] text-water">Decision Engine</h3>{incidentZoneId && <button type="button" onClick={() => setIncidentZoneId(null)} className="text-[11px] font-semibold text-slate-400 hover:text-white">CLEAR</button>}</div>
        {!incidentZoneId ? <p className="text-sm text-slate-400">No incident selected. Click a flood zone to begin analysis.</p> : loadingDecision ? <p className="animate-pulse text-sm text-slate-400">Analyzing incident parameters and calculating optimal routes...</p> : decisionError ? <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 text-sm text-rose-300">{decisionError}</div> : decision ? (
          <div className="space-y-4">
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Flood Prediction</p><div className="mt-1 flex items-end gap-2"><span className="text-2xl font-black text-white">{decision.simulation.severity_score.toFixed(0)}<span className="text-sm text-slate-500">/100</span></span><span className="mb-1 rounded bg-slate-900 px-2 py-0.5 text-[10px] font-semibold uppercase text-rose-400">{decision.prediction.confidence} confidence</span></div></div>

            <RecommendationPanel title="Dispatched Rescue Team" accent="text-emerald-400" candidate={decision.team_allocation.selected_team} empty="No team assigned" explanation={decision.team_allocation.explanation} factors={decision.team_allocation.selected_team?.reasoning_factors} details={decision.team_allocation.selected_team ? `${decision.team_allocation.selected_team.route_distance_km} km away · ETA ${decision.team_allocation.selected_team.estimated_travel_time_minutes} mins` : ""} />
            <RecommendationPanel title="Recommended Hospital" accent="text-rose-400" candidate={decision.hospital_recommendation.selected_hospital} empty="No suitable hospital" explanation={decision.hospital_recommendation.explanation} factors={decision.hospital_recommendation.selected_hospital?.reasoning_factors} details={decision.hospital_recommendation.selected_hospital ? `${decision.hospital_recommendation.selected_hospital.route_distance_km} km away · ${decision.hospital_recommendation.selected_hospital.available_capacity} beds` : ""} />
            <RecommendationPanel title="Evacuation Shelter" accent="text-amber-400" candidate={decision.shelter_recommendation.selected_shelter} empty="No suitable shelter" explanation={decision.shelter_recommendation.explanation} factors={decision.shelter_recommendation.selected_shelter?.reasoning_factors} details={decision.shelter_recommendation.selected_shelter ? `${decision.shelter_recommendation.selected_shelter.route_distance_km} km away · ${decision.shelter_recommendation.selected_shelter.available_capacity} spaces` : ""} />

            {!report ? <button type="button" onClick={generateReport} disabled={loadingReport} className="w-full rounded-lg bg-water py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400 disabled:opacity-50">{loadingReport ? "Generating..." : "Generate Incident Report"}</button> : <div className="rounded-lg border border-water/30 bg-water/5 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-water">AI Incident Report</p><pre className="mt-2 whitespace-pre-wrap font-sans text-xs text-slate-300">{report.report_content}</pre></div>}
          </div>
        ) : null}
      </div>

      <AnalyticsDashboard simulation={simulation} decision={decision} />
    </div>
  );
}

function RecommendationPanel({ title, accent, candidate, empty, explanation, factors, details }: { title: string; accent: string; candidate: { [key: string]: any } | null | undefined; empty: string; explanation: string; factors?: ReasoningFactor[]; details: string; }) {
  return <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3">
    <p className={`text-[10px] font-bold uppercase tracking-wider ${accent}`}>{title}</p>
    <p className="mt-1 font-semibold text-white">{candidate?.team_name ?? candidate?.hospital_name ?? candidate?.shelter_name ?? empty}</p>
    {details && <p className="mt-1 text-xs text-slate-400">{details}</p>}
    {candidate && <div className="mt-3 rounded-md border border-slate-700/70 bg-slate-900/50 p-2.5"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Why this was selected</p><p className="mt-1 text-[11px] leading-4 text-slate-300">{explanation}</p>{factors && factors.length > 0 && <div className="mt-2 space-y-1.5">{factors.map((factor) => <div key={factor.factor} className="flex items-center justify-between gap-3 text-[10px]"><span className="text-slate-400">{factor.factor}</span><span className="text-right text-slate-300">{factor.value} · {factor.contribution.toFixed(1)} pts</span></div>)}</div>}</div>}
  </div>;
}
