import type { DistrictProfile, FloodSimulationResult, RainfallScenario, RouteResponse, DecisionEngineResponse, IncidentReportResponse } from "./types";

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

export async function fetchRoute(startId: string, endId: string, scenario: string): Promise<RouteResponse> {
  const response = await fetch(`/api/v1/route?start_id=${startId}&end_id=${endId}&scenario=${scenario}`);
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
  return response.json();
}

export async function fetchDecisionBundle(
  zoneId: string, 
  scenario: RainfallScenario, 
  elevation: number, 
  drainage: number
): Promise<DecisionEngineResponse> {
  const formData = new FormData();
  formData.append("incident_zone_id", zoneId);
  
  let rainfall = 50.0;
  if (scenario === "severe") rainfall = 100.0;
  if (scenario === "extreme") rainfall = 200.0;
  
  formData.append("rainfall_mm", rainfall.toString());
  formData.append("elevation_m", elevation.toString());
  formData.append("drainage_score", drainage.toString());
  formData.append("previous_water_level_m", "1.5");
  
  const response = await fetch("/api/v1/decision-engine", {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`Decision engine request failed (${response.status})`);
  }
  return response.json();
}

export async function fetchReport(decision: DecisionEngineResponse): Promise<IncidentReportResponse> {
  const response = await fetch("/api/v1/generate-report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decision),
  });
  if (!response.ok) throw new Error("Failed to generate report");
  return response.json();
}
