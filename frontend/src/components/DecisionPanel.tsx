import { useEffect, useMemo, useState } from "react";
import { fetchDecisionEngine } from "../api";
import type { DecisionEngineResponse, DistrictProfile } from "../types";

interface DecisionPanelProps {
  district: DistrictProfile;
}

export function DecisionPanel({ district }: DecisionPanelProps) {
  const [incidentZoneId, setIncidentZoneId] = useState(district.zones[0]?.id ?? "");
  const [rainfallMm, setRainfallMm] = useState(120);
  const [previousWaterLevelM, setPreviousWaterLevelM] = useState(1.2);
  const [requiredSpecialty, setRequiredSpecialty] = useState("");
  const [decision, setDecision] = useState<DecisionEngineResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const zone = useMemo(
    () => district.zones.find((item) => item.id === incidentZoneId) ?? district.zones[0],
    [district.zones, incidentZoneId],
  );

  useEffect(() => {
    if (zone && !district.zones.some((item) => item.id === incidentZoneId)) {
      setIncidentZoneId(zone.id);
    }
  }, [district.zones, incidentZoneId, zone]);

  const runDecision = async () => {
    if (!zone) return;
    setLoading(true);
    setError(null);
    try {
      const result = await fetchDecisionEngine(
        zone.id,
        rainfallMm,
        zone.elevation_m,
        zone.drainage_score,
        previousWaterLevelM,
        requiredSpecialty.trim() || undefined,
      );
      setDecision(result);
    } catch (requestError: unknown) {
      setError(requestError instanceof Error ? requestError.message : "Unable to run the decision engine.");
    } finally {
      setLoading(false);
    }
  };

  const prediction = decision?.prediction;
  const hospital = decision?.hospital_recommendation.selected_hospital;
  const shelter = decision?.shelter_recommendation.selected_shelter;
  const team = decision?.team_allocation.selected_team;

  return (
    <section className="rounded-2xl border border-line bg-panel p-5 shadow-panel">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-water">Unified decision engine</p>
          <h2 className="mt-1 text-lg font-semibold text-white">Incident response recommendation</h2>
          <p className="mt-1 text-xs text-slate-400">Run prediction, simulation, routing, facility selection, and team allocation from one API call.</p>
        </div>
        {decision && <span className="rounded-full border border-rescue/30 bg-rescue/10 px-3 py-1 text-[10px] font-semibold uppercase text-rescue">Decision ready</span>}
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <label className="text-xs text-slate-400 lg:col-span-2">Incident zone
          <select value={incidentZoneId} onChange={(event) => setIncidentZoneId(event.target.value)} className="mt-1 w-full rounded-lg border border-line bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-water">
            {district.zones.map((item) => <option key={item.id} value={item.id}>{item.id} · {item.name}</option>)}
          </select>
        </label>
        <label className="text-xs text-slate-400">Rainfall (mm)
          <input type="number" min="0" max="320" value={rainfallMm} onChange={(event) => setRainfallMm(Number(event.target.value))} className="mt-1 w-full rounded-lg border border-line bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-water" />
        </label>
        <label className="text-xs text-slate-400">Water level (m)
          <input type="number" min="0" max="4" step="0.1" value={previousWaterLevelM} onChange={(event) => setPreviousWaterLevelM(Number(event.target.value))} className="mt-1 w-full rounded-lg border border-line bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-water" />
        </label>
        <label className="text-xs text-slate-400">Specialty (optional)
          <input value={requiredSpecialty} onChange={(event) => setRequiredSpecialty(event.target.value)} placeholder="paramedic" className="mt-1 w-full rounded-lg border border-line bg-slate-900 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-water" />
        </label>
      </div>

      <button type="button" disabled={loading || !zone} onClick={runDecision} className="mt-4 rounded-lg bg-water px-4 py-2 text-xs font-bold uppercase tracking-wide text-slate-950 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50">
        {loading ? "Running decision engine…" : "Run decision engine"}
      </button>

      {error && <p className="mt-3 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">{error}</p>}

      {decision && (
        <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <article className="rounded-xl border border-line bg-slate-900/60 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">Flood prediction</p><p className="mt-1 text-xl font-semibold text-white">{prediction?.predicted_flood_severity.toFixed(1)}</p><p className="text-[11px] text-slate-400">Confidence: {prediction?.confidence}</p></article>
          <article className="rounded-xl border border-line bg-slate-900/60 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">Hospital</p><p className="mt-1 truncate text-sm font-semibold text-white">{hospital?.hospital_name ?? "None suitable"}</p><p className="text-[11px] text-slate-400">{hospital ? `${hospital.suitability_score.toFixed(1)} suitability · ${hospital.route_distance_km} km` : decision.hospital_recommendation.status}</p></article>
          <article className="rounded-xl border border-line bg-slate-900/60 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">Shelter</p><p className="mt-1 truncate text-sm font-semibold text-white">{shelter?.shelter_name ?? "None suitable"}</p><p className="text-[11px] text-slate-400">{shelter ? `${shelter.suitability_score.toFixed(1)} suitability · ${shelter.available_capacity} spaces` : decision.shelter_recommendation.status}</p></article>
          <article className="rounded-xl border border-line bg-slate-900/60 p-3"><p className="text-[10px] uppercase tracking-wider text-slate-500">Rescue team</p><p className="mt-1 truncate text-sm font-semibold text-white">{team?.team_name ?? "None suitable"}</p><p className="text-[11px] text-slate-400">{team ? `${team.personnel_count} personnel · ${team.suitability_score.toFixed(1)} suitability` : decision.team_allocation.status}</p></article>
        </div>
      )}
    </section>
  );
}
