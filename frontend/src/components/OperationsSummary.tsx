import type { DecisionEngineResponse, DistrictProfile, FloodSimulationResult } from "../types";

interface OperationsSummaryProps {
  simulation: FloodSimulationResult | null;
  decision: DecisionEngineResponse | null;
  district: DistrictProfile;
}

function metricTone(value: string | number | null, tone: string) {
  return value === null ? "text-slate-500" : tone;
}

function MetricCard({ label, value, detail, tone }: { label: string; value: string | number | null; detail: string; tone: string }) {
  return (
    <div className="min-w-0 rounded-lg border border-slate-700 bg-ink/90 px-3 py-2.5 shadow-lg backdrop-blur">
      <p className="text-[9px] font-bold uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className={`mt-1 truncate text-sm font-bold ${metricTone(value, tone)}`}>{value ?? "—"}</p>
      <p className="mt-0.5 truncate text-[10px] text-slate-500">{detail}</p>
    </div>
  );
}

export function OperationsSummary({ simulation, decision, district }: OperationsSummaryProps) {
  const affectedCount = simulation?.affected_zones.length ?? 0;
  const blockedCount = simulation?.blocked_roads.length ?? 0;
  const selectedHospital = decision?.hospital_recommendation.selected_hospital;
  const selectedShelter = decision?.shelter_recommendation.selected_shelter;
  const selectedTeam = decision?.team_allocation.selected_team;
  const incidentZone = decision ? district.zones.find((zone) => zone.id === decision.incident_zone_id) : null;

  const severity = simulation?.severity_score ?? decision?.simulation.severity_score ?? null;
  const severityLabel = severity === null ? "Waiting for incident" : severity >= 80 ? "Critical" : severity >= 60 ? "High" : severity >= 35 ? "Moderate" : "Low";
  const severityTone = severity === null ? "text-slate-500" : severity >= 80 ? "text-rose-300" : severity >= 60 ? "text-orange-300" : severity >= 35 ? "text-amber-300" : "text-emerald-300";

  return (
    <section className="absolute bottom-5 left-5 right-5 z-[1000] rounded-xl border border-slate-700 bg-ink/90 p-3 shadow-xl backdrop-blur" aria-label="Operations summary">
      <div className="mb-2 flex items-center justify-between gap-3">
        <div>
          <p className="text-[9px] font-bold uppercase tracking-[0.2em] text-water">Operations Summary</p>
          <p className="mt-0.5 text-[10px] text-slate-500">
            {incidentZone ? `${incidentZone.name} · ${simulation?.scenario ?? decision?.simulation.scenario ?? "incident"} scenario` : "Select a zone to populate incident recommendations"}
          </p>
        </div>
        <span className="hidden rounded-full border border-slate-700 px-2 py-1 text-[9px] font-semibold uppercase tracking-wider text-slate-400 sm:inline-flex">Live incident state</span>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
        <MetricCard label="Flood severity" value={severity === null ? null : `${severity.toFixed(0)}/100`} detail={severityLabel} tone={severityTone} />
        <MetricCard label="Affected zones" value={simulation ? affectedCount : null} detail={simulation ? "zones impacted" : "awaiting simulation"} tone="text-amber-300" />
        <MetricCard label="Blocked roads" value={simulation ? blockedCount : null} detail={simulation ? "routes restricted" : "awaiting simulation"} tone="text-orange-300" />
        <MetricCard label="Hospital" value={selectedHospital?.hospital_name ?? null} detail={selectedHospital ? `${selectedHospital.available_capacity} beds available` : "no recommendation yet"} tone="text-rose-300" />
        <MetricCard label="Shelter" value={selectedShelter?.shelter_name ?? null} detail={selectedShelter ? `${selectedShelter.available_capacity} spaces available` : "no recommendation yet"} tone="text-amber-300" />
        <MetricCard label="Rescue team" value={selectedTeam?.team_name ?? null} detail={selectedTeam ? `${selectedTeam.personnel_count} personnel · ${selectedTeam.estimated_travel_time_minutes} min ETA` : "no assignment yet"} tone="text-emerald-300" />
      </div>
    </section>
  );
}
