import type { DecisionEngineResponse, FloodSimulationResult } from "../types";

interface OperationsSummaryProps { simulation: FloodSimulationResult | null; decision: DecisionEngineResponse | null; }

export function OperationsSummary({ simulation, decision }: OperationsSummaryProps) {
  const items = [
    { label: "Severity", value: simulation ? `${simulation.severity_score.toFixed(1)} / 100` : "—" },
    { label: "Affected zones", value: simulation ? `${simulation.affected_zones.length}` : "—" },
    { label: "Blocked roads", value: simulation ? `${simulation.blocked_roads.length}` : "—" },
    { label: "Hospital", value: decision?.hospital_recommendation.selected_hospital?.hospital_name ?? "Not selected" },
    { label: "Shelter", value: decision?.shelter_recommendation.selected_shelter?.shelter_name ?? "Not selected" },
    { label: "Rescue team", value: decision?.team_allocation.selected_team?.team_name ?? "Not assigned" },
  ];

  return <section className="mt-5 rounded-2xl border border-line bg-panel p-5 shadow-panel" aria-labelledby="ops-summary-heading">
    <div className="flex items-end justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-water">Operations summary</p><h2 id="ops-summary-heading" className="mt-1 text-xl font-semibold text-white">Incident command snapshot</h2></div><p className="text-xs text-slate-500">Single source: active decision bundle</p></div>
    <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{items.map((item) => <article key={item.label} className="rounded-xl border border-line bg-ink/40 p-4"><p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{item.label}</p><p className="mt-2 truncate text-sm font-semibold text-white" title={item.value}>{item.value}</p></article>)}</div>
  </section>;
}
