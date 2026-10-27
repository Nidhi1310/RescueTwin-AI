import { useEffect, useRef, useState } from "react";
import { ApiError, MAX_IMAGE_BYTES, fetchDecisionBundle, fetchReport, fetchSimulation, releaseDispatch } from "../api";
import type {
  DecisionEngineResponse,
  DistrictProfile,
  FallbackOption,
  FloodSimulationResult,
  IncidentReportResponse,
  RainfallScenario,
  ReasoningFactor,
} from "../types";
import { OperationalMap } from "./OperationalMap";
import { AnalyticsDashboard } from "./AnalyticsDashboard";
import { OperationsSummary } from "./OperationsSummary";

interface DecisionControllerProps { district: DistrictProfile; }
const scenarios: RainfallScenario[] = ["moderate", "severe", "extreme"];

function Reasoning({ explanation, factors }: { explanation: string; factors: ReasoningFactor[] }) {
  return <details className="mt-2 rounded-md border border-[#23415a] bg-[#07111f]/80 p-2 group"><summary className="cursor-pointer list-none text-[10px] font-bold uppercase tracking-wider text-[#22c7ff]">WHY THIS WAS SELECTED <span className="float-right text-slate-500 group-open:rotate-90">›</span></summary><p className="mt-2 text-xs leading-5 text-slate-300">{explanation}</p><div className="mt-2 space-y-1">{factors.map((factor) => <div key={factor.factor} className="flex items-center justify-between gap-2 text-[10px] text-slate-400"><span>{factor.factor}: {factor.value}</span><span className="font-semibold text-slate-200">+{factor.contribution.toFixed(1)}</span></div>)}</div></details>;
}

function friendlyError(error: unknown, fallback: string) {
  if (error instanceof ApiError) {
    if (error.status === 404) return "The selected incident is no longer available. Choose another zone.";
    if (error.status === 429) return "Too many requests. Please wait a moment and try again.";
    if (error.status >= 500) return "The backend could not complete this request. Please try again.";
    return error.message;
  }
  return error instanceof Error ? error.message : fallback;
}

function reportFilename(scenario: RainfallScenario, zoneId: string | null) {
  const zone = zoneId ?? "incident";
  return `rescuetwin-${scenario}-${zone}-incident-report.md`;
}

const confidenceTone = { high: "text-emerald-300", medium: "text-amber-300", low: "text-[#ff5964]" } as const;
const priorityTone = { routine: "text-emerald-300", urgent: "text-amber-300", critical: "text-[#ff5964]" } as const;
const card = "rounded-lg border border-[#23415a] bg-[#0b1a2a]/90 p-3";
const dangerBox = "rounded-lg border border-rose-500/30 bg-rose-500/5 p-3 text-sm text-rose-300";

function FallbackNote({ fallback }: { fallback: FallbackOption | null | undefined }) {
  if (!fallback) return null;
  return <p className="mt-2 rounded-md border border-amber-400/30 bg-amber-400/5 p-2 text-[11px] leading-4 text-amber-200">{fallback.advice}</p>;
}

function RecommendationPanel({ title, accent, candidate, empty, explanation, factors, details, fallback }: {
  title: string; accent: string; candidate: { [key: string]: any } | null | undefined; empty: string;
  explanation: string; factors?: ReasoningFactor[]; details: string; fallback?: FallbackOption | null;
}) {
  return (
    <div className={card}>
      <p className={`text-[10px] font-bold uppercase tracking-wider ${accent}`}>{title}</p>
      <p className="mt-1 font-semibold text-white">{candidate?.team_name ?? candidate?.hospital_name ?? candidate?.shelter_name ?? empty}</p>
      {details && <p className="mt-1 text-xs text-slate-400">{details}</p>}
      {candidate ? <Reasoning explanation={explanation} factors={factors ?? []} /> : <><p className="mt-1 text-xs leading-5 text-slate-400">{fallback ? explanation.replace(fallback.advice, "").trim() : explanation}</p><FallbackNote fallback={fallback} /></>}
    </div>
  );
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
  const [dispatchBusy, setDispatchBusy] = useState(false);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const reportRequestId = useRef(0);

  useEffect(() => {
    let cancelled = false;
    setLoadingSimulation(true); setSimulationError(null);
    fetchSimulation(scenario)
      .then((result) => { if (!cancelled) setSimulation(result); })
      .catch((error) => { console.error(error); if (!cancelled) { setSimulation(null); setSimulationError(friendlyError(error, "Flood simulation could not be loaded.")); } })
      .finally(() => { if (!cancelled) setLoadingSimulation(false); });
    return () => { cancelled = true; };
  }, [scenario]);

  useEffect(() => {
    reportRequestId.current += 1; // any in-flight report belongs to the previous decision
    setReport(null); setReportError(null); setCopyStatus(null); setLoadingReport(false);
    if (!incidentZoneId) { setDecision(null); setDecisionError(null); return; }
    if (!district.zones.some((z) => z.id === incidentZoneId)) return;
    const controller = new AbortController();
    setLoadingDecision(true); setDecisionError(null);
    fetchDecisionBundle(incidentZoneId, scenario, { image: imageFile, signal: controller.signal })
      .then((result) => { if (!controller.signal.aborted) setDecision(result); })
      .catch((error) => {
        if (controller.signal.aborted) return;
        console.error(error); setDecision(null);
        setDecisionError(friendlyError(error, "Unable to calculate the decision bundle. Please try again."));
      })
      .finally(() => { if (!controller.signal.aborted) setLoadingDecision(false); });
    return () => controller.abort();
  }, [incidentZoneId, scenario, district.zones, imageFile, reloadKey]);

  const handleEntityClick = (id: string) => {
    if (district.zones.some((z) => z.id === id)) { setImageFile(null); setImageError(null); setIncidentZoneId(id); }
  };

  const onImageChosen = (file: File | null) => {
    setImageError(null);
    if (file && file.size > MAX_IMAGE_BYTES) { setImageError("Image is larger than 8 MB."); return; }
    setImageFile(file);
  };

  const generateReport = () => {
    if (!decision) return;
    const requestId = ++reportRequestId.current;
    setLoadingReport(true); setReportError(null); setCopyStatus(null);
    fetchReport(decision)
      .then((result) => { if (requestId === reportRequestId.current) setReport(result); })
      .catch((error) => { console.error(error); if (requestId === reportRequestId.current) setReportError(friendlyError(error, "The incident report could not be generated.")); })
      .finally(() => { if (requestId === reportRequestId.current) setLoadingReport(false); });
  };

  const commitDispatch = () => {
    if (!incidentZoneId) return;
    setDispatchBusy(true); setDecisionError(null);
    fetchDecisionBundle(incidentZoneId, scenario, { image: imageFile, commit: true })
      .then((result) => { reportRequestId.current += 1; setReport(null); setDecision(result); })
      .catch((error) => setDecisionError(friendlyError(error, "The team could not be committed.")))
      .finally(() => setDispatchBusy(false));
  };

  const releaseTeam = () => {
    if (!incidentZoneId) return;
    setDispatchBusy(true); setDecisionError(null);
    releaseDispatch(incidentZoneId)
      .then(() => setReloadKey((key) => key + 1))
      .catch((error) => setDecisionError(friendlyError(error, "The team could not be released.")))
      .finally(() => setDispatchBusy(false));
  };

  const copyReport = async () => {
    if (!report) return;
    try { await navigator.clipboard.writeText(report.report_content); setCopyStatus("Report copied to clipboard."); }
    catch { setCopyStatus("Clipboard access is unavailable. Use Download instead."); }
  };

  const downloadReport = () => {
    if (!report) return;
    const blob = new Blob([report.report_content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = reportFilename(scenario, incidentZoneId);
    document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
    setCopyStatus("Report downloaded.");
  };

  const selectedIds = new Set<string>();
  if (incidentZoneId) selectedIds.add(incidentZoneId);
  if (decision?.hospital_recommendation.selected_hospital) selectedIds.add(decision.hospital_recommendation.selected_hospital.hospital_id);
  if (decision?.shelter_recommendation.selected_shelter) selectedIds.add(decision.shelter_recommendation.selected_shelter.shelter_id);
  if (decision?.team_allocation.selected_team) selectedIds.add(decision.team_allocation.selected_team.team_id);

  const hospital = decision?.hospital_recommendation;
  const shelter = decision?.shelter_recommendation;
  const team = decision?.team_allocation;

  return (
    <div className="relative">
      <OperationalMap zones={district.zones} hospitals={district.hospitals} shelters={district.shelters} rescueTeams={district.rescue_teams}
        hospitalRoute={decision?.hospital_route} shelterRoute={decision?.shelter_route} teamRoute={decision?.team_route}
        simulation={simulation} center={district.metadata.center} selectedIds={selectedIds} onEntityClick={handleEntityClick} />

      <div className="absolute left-4 top-4 z-[1000] w-60 rounded-xl border border-[#1a435f] bg-[#07111f]/95 p-3.5 shadow-2xl backdrop-blur-md">
        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-water">Scenario</p>
        <h3 className="mt-1 text-sm font-semibold text-white">Rainfall simulation</h3>
        <div className="mt-3 grid grid-cols-3 gap-1 rounded-lg bg-slate-900/80 p-1">
          {scenarios.map((value) => (
            <button key={value} type="button" disabled={loadingSimulation || loadingDecision}
              onClick={() => { setIncidentZoneId(null); setScenario(value); }}
              className={`rounded-md px-2 py-2 text-[10px] font-bold uppercase ${scenario === value ? "bg-[#22c7ff] text-[#03121d]" : "text-slate-300 hover:bg-slate-800"}`}>{value}</button>
          ))}
        </div>
        {simulationError
          ? <div className="mt-3 rounded-md border border-rose-500/30 bg-rose-500/5 p-2 text-[11px] text-rose-300">{simulationError}</div>
          : <p className="mt-3 text-[11px] text-slate-400">Click any <strong className="text-sky-400">zone</strong> on the map to run the decision engine.</p>}
      </div>

      <div className="absolute left-4 top-[170px] z-[1000] max-h-[490px] w-[330px] overflow-y-auto rounded-xl border border-[#1a435f] bg-[#07111f]/96 p-3.5 shadow-2xl backdrop-blur-md">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-[0.18em] text-water">Decision Engine</h3>
          {incidentZoneId && <button type="button" onClick={() => setIncidentZoneId(null)} className="text-[11px] font-semibold text-slate-400 hover:text-white">CLEAR</button>}
        </div>

        {!incidentZoneId ? <p className="text-sm text-slate-400">No incident selected. Click a flood zone to begin analysis.</p>
        : loadingDecision ? (
          <div className="space-y-2"><p className="animate-pulse text-sm text-slate-300">Analyzing incident...</p><p className="text-xs text-slate-500">Calculating safe routes and operational recommendations.</p></div>
        ) : decisionError ? (
          <div className={dangerBox}><p>{decisionError}</p>
            <button type="button" onClick={() => setReloadKey((key) => key + 1)} className="mt-3 rounded-md border border-rose-400/30 px-3 py-1.5 text-xs font-semibold text-rose-200 hover:bg-rose-500/10">Retry analysis</button></div>
        ) : decision && hospital && shelter && team ? (
          <div className="space-y-4">
            <div className={card}>
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">ML Flood Prediction</p>
                <span className={`text-[10px] font-bold uppercase ${priorityTone[decision.priority]}`}>{decision.priority} priority</span>
              </div>
              <div className="mt-1 flex items-end gap-2">
                <span className="text-2xl font-black text-white">{decision.prediction.predicted_flood_severity.toFixed(0)}<span className="text-sm text-slate-500">/100</span></span>
                <span className={`mb-1 rounded bg-slate-900 px-2 py-0.5 text-[10px] font-semibold uppercase ${confidenceTone[decision.prediction.confidence]}`}>{decision.prediction.confidence} confidence</span>
              </div>
              <p className="mt-1 text-[11px] text-slate-400">Scenario simulation (district): <strong className="text-slate-200">{decision.simulation.severity_score.toFixed(0)}/100</strong>
                {decision.prediction.expected_error_points !== null && <> · model error ±{decision.prediction.expected_error_points} pts</>}</p>
              <p className="mt-2 text-xs leading-5 text-slate-400">{decision.prediction.explanation}</p>
              <div className="mt-3 grid grid-cols-2 gap-2">
                {Object.entries(decision.prediction.input_factors).map(([factor, value]) => (
                  <div key={factor} className="rounded-md border border-slate-700 bg-slate-900/60 px-2 py-2">
                    <p className="text-[9px] uppercase tracking-wider text-slate-500">{factor.replace(/_/g, " ")}</p>
                    <p className="mt-1 text-xs font-semibold text-slate-200">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {decision.incident_isolated && <div className={dangerBox}><p className="text-xs font-bold uppercase tracking-wider">Incident zone isolated</p><p className="mt-1 text-xs">Every access road is flood-blocked. See the fallback options below.</p></div>}
            {decision.warnings.length > 0 && (
              <div className="rounded-lg border border-amber-400/30 bg-amber-400/5 p-3"><p className="text-[10px] font-bold uppercase tracking-wider text-amber-300">Warnings</p>
                <ul className="mt-1 list-disc space-y-1 pl-4 text-[11px] leading-4 text-amber-100">{decision.warnings.map((w) => <li key={w}>{w}</li>)}</ul></div>
            )}

            <div className={card}>
              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Incident image (optional)</p>
              <input type="file" accept="image/png,image/jpeg,image/webp,image/gif,image/bmp" onChange={(event) => onImageChosen(event.target.files?.[0] ?? null)} className="mt-2 block w-full text-[11px] text-slate-300 file:mr-2 file:rounded file:border-0 file:bg-slate-700 file:px-2 file:py-1 file:text-slate-100" />
              {imageError && <p className="mt-1 text-[11px] text-rose-300">{imageError}</p>}
              {decision.damage_assessment && (
                <div className="mt-2 text-xs text-slate-300">
                  <p>Indicative level: <strong className="uppercase text-white">{decision.damage_assessment.damage_level}</strong> · {decision.damage_assessment.water_coverage_pct}% water-coloured</p>
                  <p className="mt-1 text-[10px] leading-4 text-slate-500">{decision.damage_assessment.disclaimer}</p>
                </div>
              )}
            </div>

            <RecommendationPanel title="Dispatched Rescue Team" accent="text-[#22d3a7]" candidate={team.selected_team} empty="No team can be dispatched by road"
              explanation={team.explanation} factors={team.selected_team?.reasoning_factors} fallback={team.fallback}
              details={team.selected_team ? `${team.selected_team.route_distance_km} km away · ETA ${team.selected_team.estimated_travel_time_minutes} mins${decision.dispatch_committed ? " · COMMITTED" : " · proposed"}` : ""} />
            {team.selected_team && (
              decision.dispatch_committed
                ? <button type="button" disabled={dispatchBusy} onClick={releaseTeam} className="w-full rounded-lg border border-amber-400/40 py-2 text-sm font-semibold text-amber-200 disabled:opacity-50">{dispatchBusy ? "Releasing..." : "Release team"}</button>
                : <button type="button" disabled={dispatchBusy} onClick={commitDispatch} className="w-full rounded-lg border border-[#22d3a7]/50 py-2 text-sm font-semibold text-[#22d3a7] disabled:opacity-50">{dispatchBusy ? "Committing..." : "Commit dispatch"}</button>
            )}

            <RecommendationPanel title="Recommended Hospital" accent="text-rose-400" candidate={hospital.selected_hospital} empty="No suitable hospital" explanation={hospital.explanation}
              factors={hospital.selected_hospital?.reasoning_factors} fallback={hospital.fallback}
              details={hospital.selected_hospital ? `${hospital.selected_hospital.route_distance_km} km away · ${hospital.selected_hospital.available_capacity} beds` : ""} />
            <RecommendationPanel title="Evacuation Shelter" accent="text-[#ffc233]" candidate={shelter.selected_shelter} empty="No suitable shelter" explanation={shelter.explanation}
              factors={shelter.selected_shelter?.reasoning_factors} fallback={shelter.fallback}
              details={shelter.selected_shelter ? `${shelter.selected_shelter.route_distance_km} km away · ${shelter.selected_shelter.available_capacity} spaces` : ""} />

            {reportError && <div className={dangerBox}><p>{reportError}</p>
              <button type="button" onClick={generateReport} className="mt-3 rounded-md border border-rose-400/30 px-3 py-1.5 text-xs font-semibold text-rose-200 hover:bg-rose-500/10">Retry report</button></div>}
            {!report && !reportError && (
              <button type="button" onClick={generateReport} disabled={loadingReport} className="w-full rounded-lg bg-water py-2 text-sm font-semibold text-slate-950 disabled:opacity-50">{loadingReport ? "Generating..." : "Generate Incident Report"}</button>
            )}
            {report && (
              <div className="rounded-lg border border-[#22c7ff]/30 bg-[#22c7ff]/5 p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-water">Incident Report</p>
                  <div className="flex gap-2">
                    <button type="button" onClick={copyReport} className="rounded-md border border-slate-600 px-2 py-1 text-[10px] font-semibold text-slate-300 hover:bg-slate-800">Copy</button>
                    <button type="button" onClick={downloadReport} className="rounded-md border border-[#22c7ff]/40 px-2 py-1 text-[10px] font-semibold text-[#22c7ff] hover:bg-water/10">Download</button>
                  </div>
                </div>
                <pre className="mt-2 whitespace-pre-wrap font-sans text-xs text-slate-300">{report.report_content}</pre>
                {copyStatus && <p className="mt-2 text-[10px] text-slate-500">{copyStatus}</p>}
              </div>
            )}
          </div>
        ) : null}
      </div>

      <OperationsSummary simulation={simulation} decision={decision} district={district} />
      <AnalyticsDashboard simulation={simulation} decision={decision} />
    </div>
  );
}
