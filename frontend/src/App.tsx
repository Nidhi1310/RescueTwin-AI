import { useEffect, useState } from "react";

import { fetchDistrict } from "./api";
import { RoutingController } from "./components/RoutingController";
import type { DistrictProfile } from "./types";

function LoadingState() {
  return <div className="grid min-h-screen place-items-center bg-ink text-slate-300"><p className="animate-pulse text-sm tracking-wide">Loading district operational data…</p></div>;
}

function ErrorState({ message }: { message: string }) {
  return <div className="grid min-h-screen place-items-center bg-ink p-6 text-center"><div><p className="text-lg font-semibold text-white">District data is unavailable</p><p className="mt-2 text-sm text-slate-400">{message} Start the backend on port 8000 and reload this page.</p></div></div>;
}

export default function App() {
  const [district, setDistrict] = useState<DistrictProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDistrict().then(setDistrict).catch((requestError: unknown) => {
      setError(requestError instanceof Error ? requestError.message : "Unknown API error.");
    });
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!district) return <LoadingState />;

  const totalPopulation = district.zones.reduce((total, zone) => total + zone.population, 0);
  return (
    <main className="min-h-screen bg-ink text-slate-100">
      <header className="border-b border-line bg-[#0d1728]/90 px-6 py-5 backdrop-blur lg:px-10">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-4">
          <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-rescue text-lg font-black text-emerald-950">R</div><div><p className="text-lg font-bold tracking-tight text-white">RescueTwin AI</p><p className="text-xs text-slate-400">Flood Response Command Center</p></div></div>
          <div className="hidden rounded-full border border-rescue/30 bg-rescue/10 px-3 py-1.5 text-xs font-semibold text-rescue sm:block">● System ready</div>
        </div>
      </header>
      <div className="mx-auto max-w-[1500px] px-6 py-8 lg:px-10">
        <section className="mb-8 flex flex-col justify-between gap-4 lg:flex-row lg:items-end"><div><p className="text-sm font-semibold uppercase tracking-[0.2em] text-water">{district.metadata.region}, {district.metadata.country}</p><h1 className="mt-2 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{district.metadata.name}</h1><p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400">{district.metadata.description}</p></div><p className="text-sm text-slate-500">Local timezone · {district.metadata.timezone}</p></section>
        <section className="mb-8 grid grid-cols-2 gap-3 lg:grid-cols-4">
          {[['Flood zones', district.zones.length], ['Residents', totalPopulation.toLocaleString()], ['Care facilities', district.hospitals.length + district.shelters.length], ['Rescue teams', district.rescue_teams.length]].map(([label, value]) => <article key={String(label)} className="rounded-xl border border-line bg-panel p-4"><p className="text-xs uppercase tracking-wider text-slate-500">{label}</p><p className="mt-2 text-2xl font-semibold text-white">{value}</p></article>)}
        </section>
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
          <RoutingController district={district} />
          <aside className="space-y-4"><section className="rounded-2xl border border-line bg-panel p-5 shadow-panel"><p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Facilities</p><div className="mt-4 space-y-3">{[...district.hospitals, ...district.shelters].map((facility) => <div key={facility.id} className="border-b border-line pb-3 last:border-0 last:pb-0"><div className="flex items-center justify-between gap-2"><p className="text-sm font-medium text-white">{facility.name}</p><span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] uppercase text-slate-300">{facility.type}</span></div><p className="mt-1 text-xs text-slate-500">{facility.current_occupancy} / {facility.capacity} occupied</p></div>)}</div></section><section className="rounded-2xl border border-line bg-panel p-5 shadow-panel"><p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Teams</p><div className="mt-4 space-y-3">{district.rescue_teams.map((team) => <div key={team.id} className="flex justify-between gap-3"><div><p className="text-sm font-medium text-white">{team.name}</p><p className="mt-1 text-xs text-slate-500">{team.personnel_count} personnel · {team.specialties[0]}</p></div><span className="h-fit rounded bg-rescue/10 px-2 py-1 text-[10px] font-semibold uppercase text-rescue">{team.status}</span></div>)}</div></section></aside>
        </div>
      </div>
    </main>
  );
}
