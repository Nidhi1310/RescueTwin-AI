import type { DistrictProfile, FloodSimulationResult, RainfallScenario, RouteResponse } from "./types";

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
