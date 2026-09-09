import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ReactNode } from "react";

import type { DecisionEngineResponse, FloodSimulationResult } from "../types";

interface AnalyticsDashboardProps {
  simulation: FloodSimulationResult | null;
  decision: DecisionEngineResponse | null;
}

const SEVERITY_COLORS = { monitoring: "#38bdf8", affected: "#f59e0b", severe: "#ef4444" };
const IMPACT_COLORS = ["#ef4444", "#334155"];

export function AnalyticsDashboard({ simulation, decision }: AnalyticsDashboardProps) {
  if (!simulation) {
    return (
      <section className="mt-6 rounded-2xl border border-line bg-panel p-5 shadow-panel">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Incident analytics</p>
        <p className="mt-3 text-sm text-slate-400">Loading current scenario analytics…</p>
      </section>
    );
  }

  const severityData = simulation.zone_impacts.map((impact) => ({
    name: impact.zone_name,
    severity: impact.severity_score,
    affected: impact.affected,
  }));
  const affectedCount = simulation.affected_zones.length;
  const impactData = [
    { name: "Affected", value: affectedCount },
    { name: "Monitoring", value: simulation.zone_impacts.length - affectedCount },
  ];
  const selectedHospital = decision?.hospital_recommendation.selected_hospital;
  const selectedShelter = decision?.shelter_recommendation.selected_shelter;
  const selectedTeam = decision?.team_allocation.selected_team;

  return (
    <section className="mt-6 rounded-2xl border border-line bg-panel p-5 shadow-panel" aria-labelledby="analytics-heading">
      <div className="flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water">Incident analytics</p>
          <h2 id="analytics-heading" className="mt-1 text-xl font-semibold text-white">{simulation.scenario} scenario overview</h2>
        </div>
        <p className="text-sm text-slate-400">District severity: <span className="font-semibold text-white">{simulation.severity_score.toFixed(1)} / 100</span></p>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-3">
        <Metric label="Affected zones" value={`${affectedCount} / ${simulation.zone_impacts.length}`} context="Flood impact" />
        <Metric label="Blocked roads" value={String(simulation.blocked_roads.length)} context="Routing constraints" />
        <Metric label="Rainfall intensity" value={`${Math.round(simulation.rainfall_intensity * 100)}%`} context="Scenario input" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.7fr)_minmax(260px,0.8fr)]">
        <ChartPanel title="Flood severity by zone">
          <div className="h-72" role="img" aria-label="Bar chart showing flood severity by zone">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData} margin={{ top: 8, right: 10, left: -18, bottom: 48 }}>
                <CartesianGrid stroke="#25334e" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" angle={-35} textAnchor="end" interval={0} tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#0b1220", border: "1px solid #25334e", borderRadius: "8px" }} labelStyle={{ color: "#e2e8f0" }} itemStyle={{ color: "#e2e8f0" }} formatter={(value) => [`${Number(value).toFixed(1)} / 100`, "Severity"]} />
                <Bar dataKey="severity" radius={[4, 4, 0, 0]}>
                  {severityData.map((entry) => <Cell key={entry.name} fill={entry.severity >= 70 ? SEVERITY_COLORS.severe : entry.affected ? SEVERITY_COLORS.affected : SEVERITY_COLORS.monitoring} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartPanel>

        <ChartPanel title="Zone impact distribution">
          <div className="h-72" role="img" aria-label="Pie chart showing affected and monitoring zones">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={impactData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={92} paddingAngle={3}>
                  {impactData.map((entry, index) => <Cell key={entry.name} fill={IMPACT_COLORS[index]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#0b1220", border: "1px solid #25334e", borderRadius: "8px" }} itemStyle={{ color: "#e2e8f0" }} />
                <Legend wrapperStyle={{ color: "#cbd5e1", fontSize: "12px" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartPanel>
      </div>

      <div className="mt-6 border-t border-line pt-5">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Recommendation summary</p>
        {decision ? (
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <RecommendationCard label="Hospital" value={selectedHospital?.hospital_name ?? "No suitable hospital"} detail={selectedHospital ? `${selectedHospital.route_distance_km} km · ${selectedHospital.available_capacity} beds` : "Check operational constraints"} accent="text-rose-400" />
            <RecommendationCard label="Shelter" value={selectedShelter?.shelter_name ?? "No suitable shelter"} detail={selectedShelter ? `${selectedShelter.route_distance_km} km · ${selectedShelter.available_capacity} spaces` : "Check operational constraints"} accent="text-amber-400" />
            <RecommendationCard label="Rescue team" value={selectedTeam?.team_name ?? "No team assigned"} detail={selectedTeam ? `${selectedTeam.route_distance_km} km · ETA ${selectedTeam.estimated_travel_time_minutes} min` : "Select an incident zone"} accent="text-emerald-400" />
          </div>
        ) : (
          <p className="mt-3 text-sm text-slate-400">Select an incident zone on the map to populate recommendation analytics.</p>
        )}
      </div>
    </section>
  );
}

function Metric({ label, value, context }: { label: string; value: string; context: string }) {
  return <article className="rounded-xl border border-line bg-ink/40 p-4"><p className="text-xs uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 text-2xl font-semibold text-white">{value}</p><p className="mt-1 text-xs text-slate-400">{context}</p></article>;
}

function ChartPanel({ title, children }: { title: string; children: ReactNode }) {
  return <article className="rounded-xl border border-line bg-ink/30 p-4"><h3 className="text-sm font-semibold text-white">{title}</h3><div className="mt-3">{children}</div></article>;
}

function RecommendationCard({ label, value, detail, accent }: { label: string; value: string; detail: string; accent: string }) {
  return <article className="rounded-xl border border-line bg-ink/40 p-4"><p className={`text-xs font-bold uppercase tracking-wider ${accent}`}>{label}</p><p className="mt-2 text-sm font-semibold text-white">{value}</p><p className="mt-1 text-xs text-slate-400">{detail}</p></article>;
}
