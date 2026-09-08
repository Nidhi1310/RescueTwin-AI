import type {
  DecisionEngineResponse,
  DistrictProfile,
  FloodSimulationResult,
  RainfallScenario,
  RouteResponse,
} from "./types";

export async function fetchDistrict(): Promise<DistrictProfile> {
  const response = await fetch("/api/v1/district");
  if (!response.ok) {
    throw new Error(`District request failed (${response.status}).`);
  }
  return (await response.json()) as DistrictProfile;
}

export async function fetchSimulation(scenario: RainfallScenario): Promise<FloodSimulationResult> {
  const response = await fetch(`/api/v1/simulate?scenario=${scenario}`);
  if (!response.ok) {
    throw new Error(`Flood simulation request failed (${response.status}).`);
  }
  return (await response.json()) as FloodSimulationResult;
}

export async function fetchRoute(startId: string, endId: string, scenario: RainfallScenario): Promise<RouteResponse> {
  const response = await fetch(`/api/v1/route?start_id=${encodeURIComponent(startId)}&end_id=${encodeURIComponent(endId)}&scenario=${scenario}`);
  if (!response.ok) throw new Error(`Route request failed (${response.status}).`);
  return (await response.json()) as RouteResponse;
}

export async function fetchDecisionEngine(
  incidentZoneId: string,
  rainfallMm: number,
  elevationM: number,
  drainageScore: number,
  previousWaterLevelM: number,
  requiredSpecialty?: string,
): Promise<DecisionEngineResponse> {
  const form = new FormData();
  form.append("incident_zone_id", incidentZoneId);
  form.append("rainfall_mm", String(rainfallMm));
  form.append("elevation_m", String(elevationM));
  form.append("drainage_score", String(drainageScore));
  form.append("previous_water_level_m", String(previousWaterLevelM));
  if (requiredSpecialty) form.append("required_specialty", requiredSpecialty);

  const response = await fetch("/api/v1/decision-engine", {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Decision engine request failed (${response.status}): ${detail}`);
  }
  return (await response.json()) as DecisionEngineResponse;
}

export async function generateIncidentReport(decision: DecisionEngineResponse): Promise<{ report_content: string; generated_at: string }> {
  const response = await fetch("/api/v1/generate-report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decision),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Incident report request failed (${response.status}): ${detail}`);
  }
  return (await response.json()) as { report_content: string; generated_at: string };
}
