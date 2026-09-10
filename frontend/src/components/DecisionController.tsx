import { useEffect, useState } from "react";
import { fetchDecisionBundle, fetchSimulation, fetchReport, ApiError } from "../api";
import type { DistrictProfile, RainfallScenario, FloodSimulationResult, DecisionEngineResponse, IncidentReportResponse, ReasoningFactor } from "../types";
import { OperationalMap } from "./OperationalMap";
import { AnalyticsDashboard } from "./AnalyticsDashboard";
import { OperationsSummary } from "./OperationsSummary";

interface DecisionControllerProps { district: DistrictProfile; }
const scenarios: RainfallScenario[] = ["moderate", "severe", "extreme"];

function Reasoning({ explanation, factors }: { explanation: string; factors: ReasoningFactor[] }) {
  return <div className="mt-2 rounded-md border border-slate-700 bg-slate-900/60 p-2"><p className="text-[10px] font-bold uppercase tracking-wider text-water">Why this was selected</p><p className="mt-1 text-xs leading-5 text-slate-300">{explanation}</p><div className="mt-2 space-y-1">{factors.map((factor) => <div key={factor.factor} className="flex items-center justify-between gap-2 text-[10px] text-slate-400"><span>{factor.factor}: {factor.value}</span><span className="font-semibold text-slate-200">+{factor.contribution.toFixed(1)}</span></div>)}</div></div>;
}

function friendlyError(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    if (error.status === 404) return "The selected incident is no longer available. Choose another zone.";
    if (error.status >= 500) return "The backend could not complete this request. Please try again.";
    return error.message;
  }
  return error instanceof Error ? error.message : fallback;
}

function reportFilename(scenario: RainfallScenario, zoneId: string | null) {
  const zone = zoneId ?? "incident";
  return `rescuetwin-${scenario}-${zone}-incident-report.txt`;
}

export function DecisionController({ district }: DecisionControllerProps) {
  const [incidentZoneId, setIncidentZoneId] = useState<string | null>(null);
  const [decision, setDecision] = useState<DecisionEngineResponse | null>(null);
  const [report, setReport] = useState<IncidentReportResponse | null>(null);
  const [scenario, setScenario] = useState<RainfallScenario>("moderate");
  const [simulation, setSimulation] = useState<FloodSimulationResult | null>(null);
  const [loadingSimulation, setLoadingSimulation] = useState(true);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [loadingDecision, setLoadingDecision] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingSimulation(true); setSimulationError(null);
    fetchSimulation(scenario).then((result) => { if (!cancelled) setSimulation(result); }).catch((error) => { console.error(error); if (!cancelled) { setSimulation(null); setSimulationError(friendlyError(error, "Flood simulation could not be loaded.")); } }).finally(() => { if (!cancelled) setLoadingSimulation(false); });
    return () => { cancelled = true; };
  }, [scenario]);

  useEffect(() => {
    if (!incidentZoneId) { setDecision(null); setReport(null); setDecisionError(null); setReportError(null); setCopyStatus(null); return; }
    const zone = district.zones.find((z) => z.id === incidentZoneId);
    if (!zone) return;
    let cancelled = false;
    setLoadingDecision(true); setReport(null); setDecisionError(null); setReportError(null); setCopyStatus(null);
    fetchDecisionBundle(zone.id, scenario, zone.elevation_m, zone.drainage_score).then((result) => { if (!cancelled) setDecision(result); }).catch((error) => { console.error(error); if (!cancelled) { setDecision(null); setDecisionError(friendlyError(error, "Unable to calculate the decision bundle. Please try again.")); } }).finally(() => { if (!cancelled) setLoadingDecision(false); });
    return () => { cancelled = true; };
  }, [incidentZoneId, scenario, district.zones]);

  const handleEntityClick = (id: string) => { if (district.zones.some((z) => z.id === id)) setIncidentZoneId(id); };
  const generateReport = () => { if (!decision) return; setLoadingReport(true); setReportError(null); setCopyStatus(null); fetchReport(decision).then(setReport).catch((error) => { console.error(error); setReportError(friendlyError(error, "The incident report could not be generated.")); }).finally(() => setLoadingReport(false)); };
  const copyReport = async () => { if (!report) return; try { await navigator.clipboard.writeText(report.report_content); setCopyStatus("Report copied to clipboard."); } catch { setCopyStatus("Clipboard access is unavailable. Use Download instead."); } };
  const downloadReport = () => { if (!report) return; const blob = new Blob([report.report_content], { type: "text/plain;charset=utf-8" }); const url = URL.createObjectURL(blob); const anchor = document.createElement("a"); anchor.href = url; anchor.download = reportFilename(scenario, incidentZoneId); document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url); setCopyStatus("Report downloaded."); };

  const selectedIds = new Set<string>();
  if (incidentZoneId) selectedIds.add(incidentZoneId);
  if (decision?.hospital_recommendation.selected_hospital) selectedIds.add(decision.hospital_recommendation.selected_hospital.hospital_id);
  if (decision?.shelter_recommendation.selected_shelter) selectedIds.add(decision.shelter_recommendation.selected_shelter.shelter_id);
  if (decision?.team_allocation.selected_team) selectedIds.add(decision.team_allocation.selected_team.team_id);

  return <div className="relative"><OperationalMap zones={district.zones} hospitals={district.hospitals} shelters={district.shelters} rescueTeams={district.rescue_teams} hospitalRoute={decision?.hospital_route} shelterRoute={decision?.shelter_route} teamRoute={decision?.team_route} simulation={simulation} center={district.metadata.center} selectedIds={selectedIds} onEntityClick={handleEntityClick} />
    <div className="absolute left-5 top-5 z-[1000] w-64 rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur"><p className="text-[10px] font-bold uppercase tracking-[0.18em] text-water">Scenario</p><h3 className="mt-1 text-sm font-semibold text-white">Rainfall simulation</h3><div className="mt-3 grid grid-cols-3 gap-1 rounded-lg bg-slate-900/80 p-1">{scenarios.map((value) => <button key={value} type="button" disabled={loadingSimulation || loadingDecision} onClick={() => { setIncidentZoneId(null); setScenario(value); }} className={`rounded-md px-2 py-2 text-[10px] font-bold uppercase ${scenario === value ? "bg-water text-slate-950" : "text-slate-300 hover:bg-slate-800"}`}>{value}</button>)}</div>{simulationError ? <div className="mt-3 rounded-md border border-rose-500/30 bg-rose-500/5 p-2 text-[11px] text-rose-300">{simulationError}</div> : <p className="mt-3 text-[11px] text-slate-400">Click any <strong className="text-sky-400">zone</strong> on the map to run the decision engine.</p>}</div>
    <div className="absolute right-5 top-5 z-[1000] w-[340px] max-h-[85vh] overflow-y-auto rounded-xl border border-slate-700 bg-ink/95 p-4 shadow-xl backdrop-blur"><div className="mb-3 flex items-center justify-between"><h3 className="text-xs font-bold uppercase tracking-[0.18em] text-water">Decision Engine</h3>{incidentZoneId && <button type="button" onClick={() => setIncidentZoneId(null)} className="text-[11px] font-semibold text-slate-400 hover:text-white">CLEAR</button>}</div>{!incidentZoneId ? <p className="text-sm text-slate-400">No incident selected. Click a flood zone to begin analysis.</p> : loadingDecision ? <div className="space-y-2"><p className="animate-pulse text-sm text-slate-300">Analyzing incident...</p><p className="text-xs text-slate-500">Calculating safe routes and operational recommendations.</p></div> : decisionError ? <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 text-sm text-rose-300"><p>{decisionError}</p><button type="button" onClick={() => { const id = incidentZoneId; setIncidentZoneId(null); window.setTimeout(() => setIncidentZoneId(id), 0); }} className="mt-3 rounded-md border border-rose-400/30 px-3 py-1.5 text-xs font-semibold text-rose-200 hover:bg-rose-500/10">Retry analysis</button></div> : decision ? <div className="space-y-4"><div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Flood Prediction</p><div className="mt-1 flex items-end gap-2"><span className="text-2xl font-black text-white">{decision.simulation.severity_score.toFixed(0)}<span className="text-sm text-slate-500">/100</span></span><span className="mb-1 rounded bg-slate-900 px-2 py-0.5 text-[10px] font-semibold uppercase text-rose-400">{decision.prediction.confidence} confidence</span></div></div>{decision.team_allocation.selected_team && <RecommendationPanel title="Dispatched Rescue Team" accent="text-emerald-400" candidate={decision.team_allocation.selected_team} empty="No team assigned" explanation={decision.team_allocation.explanation} factors={decision.team_allocation.selected_team.reasoning_factors} details={`${decision.team_allocation.selected_team.route_distance_km} km away · ETA ${decision.team_allocation.selected_team.estimated_travel_time_minutes} mins`} />}<RecommendationPanel title="Recommended Hospital" accent="text-rose-400" candidate={decision.hospital_recommendation.selected_hospital} empty="No suitable hospital" explanation={decision.hospital_recommendation.explanation} factors={decision.hospital_recommendation.selected_hospital?.reasoning_factors} details={decision.hospital_recommendation.selected_hospital ? `${decision.hospital_recommendation.selected_hospital.route_distance_km} km away · ${decision.hospital_recommendation.selected_hospital.available_capacity} beds` : ""} /><RecommendationPanel title="Evacuation Shelter" accent="text-amber-400" candidate={decision.shelter_recommendation.selected_shelter} empty="No suitable shelter" explanation={decision.shelter_recommendation.explanation} factors={decision.shelter_recommendation.selected_shelter?.reasoning_factors} details={decision.shelter_recommendation.selected_shelter ? `${decision.shelter_recommendation.selected_shelter.route_distance_km} km away · ${decision.shelter_recommendation.selected_shelter.available_capacity} spaces` : ""} />{reportError && <div className="rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 text-sm text-rose-300"><p>{reportError}</p><button type="button" onClick={generateReport} className="mt-3 rounded-md border border-rose-400/30 px-3 py-1.5 text-xs font-semibold text-rose-200 hover:bg-rose-500/10">Retry report</button></div>}{!report && !reportError ? <button type="button" onClick={generateReport} disabled={loadingReport} className="w-full rounded-lg bg-water py-2 text-sm font-semibold text-slate-950 disabled:opacity-50">{loadingReport ? "Generating..." : "Generate Incident Report"}</button> : null}{report && <div className="rounded-lg border border-water/30 bg-water/5 p-3"><div className="flex items-center justify-between gap-2"><p className="text-[10px] font-bold uppercase tracking-wider text-water">AI Incident Report</p><div className="flex gap-2"><button type="button" onClick={copyReport} className="rounded-md border border-slate-600 px-2 py-1 text-[10px] font-semibold text-slate-300 hover:bg-slate-800">Copy</button><button type="button" onClick={downloadReport} className="rounded-md border border-water/40 px-2 py-1 text-[10px] font-semibold text-water hover:bg-water/10">Download</button></div></div><pre className="mt-2 whitespace-pre-wrap font-sans text-xs text-slate-300">{report.report_content}</pre>{copyStatus && <p className="mt-2 text-[10px] text-slate-500">{copyStatus}</p>}</div>}</div> : null}</div>
    <OperationsSummary simulation={simulation} decision={decision} district={district} />
    <AnalyticsDashboard simulation={simulation} decision={decision} /></div>;
}

function RecommendationPanel({ title, accent, candidate, empty, explanation, factors, details }: { title: string; accent: string; candidate: { [key: string]: any } | null | undefined; empty: string; explanation: string; factors?: ReasoningFactor[]; details: string }) { return <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3"><p className={`text-[10px] font-bold uppercase tracking-wider ${accent}`}>{title}</p><p className="mt-1 font-semibold text-white">{candidate?.team_name ?? candidate?.hospital_name ?? candidate?.shelter_name ?? empty}</p>{details && <p className="mt-1 text-xs text-slate-400">{details}</p>}{candidate && <Reasoning explanation={explanation} factors={factors ?? []} />}</div>; }
