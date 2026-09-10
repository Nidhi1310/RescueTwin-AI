import type {
  DecisionEngineResponse,
  DistrictProfile,
  FloodSimulationResult,
  IncidentReportResponse,
  RainfallScenario,
  RouteResponse,
} from "./types";

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(message: string, status: number, code = "api_error") {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

async function requestError(response: Response, fallback: string): Promise<ApiError> {
  try {
    const payload = (await response.json()) as {
      detail?: string;
      message?: string;
      error?: string;
    };
    const message = payload.message ?? payload.detail ?? fallback;
    return new ApiError(message, response.status, payload.error ?? "api_error");
  } catch {
    return new ApiError(fallback, response.status);
  }
}

export async function fetchDistrict(): Promise<DistrictProfile> {
  const response = await fetch("/api/v1/district");
  if (!response.ok) throw await requestError(response, "District data is unavailable.");
  return (await response.json()) as DistrictProfile;
}

export async function fetchSimulation(scenario: RainfallScenario): Promise<FloodSimulationResult> {
  const response = await fetch(`/api/v1/simulate?scenario=${scenario}`);
  if (!response.ok) throw await requestError(response, "Flood simulation could not be loaded.");
  return (await response.json()) as FloodSimulationResult;
}

export async function fetchRoute(startId: string, endId: string, scenario: string): Promise<RouteResponse> {
  const response = await fetch(`/api/v1/route?start_id=${startId}&end_id=${endId}&scenario=${scenario}`);
  if (!response.ok) throw await requestError(response, "A safe route could not be calculated.");
  return (await response.json()) as RouteResponse;
}

export async function fetchDecisionBundle(
  zoneId: string,
  scenario: RainfallScenario,
  elevation: number,
  drainage: number,
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

  if (!response.ok) throw await requestError(response, "Decision analysis could not be completed.");
  return (await response.json()) as DecisionEngineResponse;
}

export async function fetchReport(decision: DecisionEngineResponse): Promise<IncidentReportResponse> {
  const response = await fetch("/api/v1/generate-report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decision),
  });
  if (!response.ok) throw await requestError(response, "The incident report could not be generated.");
  return (await response.json()) as IncidentReportResponse;
}
