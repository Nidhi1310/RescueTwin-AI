const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

const API_KEY = (import.meta.env.VITE_API_KEY as string | undefined) ?? "";
export const MAX_IMAGE_BYTES = 8 * 1024 * 1024;

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

// A static SPA cannot keep a secret: VITE_API_KEY only deters casual use. Use real auth (e.g. an
// authenticating gateway) for any non-demo deployment.
function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  if (API_KEY) headers.set("X-API-Key", API_KEY);
  return fetch(apiUrl(path), { ...init, headers });
}

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
  const response = await apiFetch("/api/v1/district");
  if (!response.ok) throw await requestError(response, "District data is unavailable.");
  return (await response.json()) as DistrictProfile;
}

export async function fetchSimulation(scenario: RainfallScenario): Promise<FloodSimulationResult> {
  const response = await apiFetch(`/api/v1/simulate?scenario=${encodeURIComponent(scenario)}`);
  if (!response.ok) throw await requestError(response, "Flood simulation could not be loaded.");
  return (await response.json()) as FloodSimulationResult;
}

export async function fetchRoute(startId: string, endId: string, scenario: string): Promise<RouteResponse> {
  const response = await apiFetch(`/api/v1/route?start_id=${encodeURIComponent(startId)}&end_id=${encodeURIComponent(endId)}&scenario=${encodeURIComponent(scenario)}`);
  if (!response.ok) throw await requestError(response, "A safe route could not be calculated.");
  return (await response.json()) as RouteResponse;
}

export interface DecisionOptions {
  image?: File | null;
  commit?: boolean;
  signal?: AbortSignal;
}

/**
 * The backend is authoritative: the client sends only the incident zone and the selected scenario.
 * Zone elevation/drainage come from district data and rainfall/water level from the scenario preset,
 * so the UI never fabricates environmental inputs.
 */
export async function fetchDecisionBundle(
  zoneId: string,
  scenario: RainfallScenario,
  options: DecisionOptions = {},
): Promise<DecisionEngineResponse> {
  const formData = new FormData();
  formData.append("incident_zone_id", zoneId);
  formData.append("scenario", scenario);
  if (options.commit) formData.append("commit", "true");
  if (options.image) formData.append("file", options.image);

  const response = await apiFetch("/api/v1/decision-engine", { method: "POST", body: formData, signal: options.signal });
  if (!response.ok) throw await requestError(response, "Decision analysis could not be completed.");
  return (await response.json()) as DecisionEngineResponse;
}

export async function releaseDispatch(zoneId: string): Promise<void> {
  const response = await apiFetch(`/api/v1/dispatch/${encodeURIComponent(zoneId)}`, { method: "DELETE" });
  if (!response.ok && response.status !== 404) throw await requestError(response, "The team could not be released.");
}

export async function fetchReport(decision: DecisionEngineResponse): Promise<IncidentReportResponse> {
  const response = await apiFetch("/api/v1/generate-report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decision),
  });
  if (!response.ok) throw await requestError(response, "The incident report could not be generated.");
  return (await response.json()) as IncidentReportResponse;
}

export const EXPECTED_API_VERSION = "0.2.0";

/** Returns the backend version, or null when the backend is an old build that does not report one. */
export async function fetchApiVersion(): Promise<string | null> {
  try {
    const response = await apiFetch("/api/v1/health");
    if (!response.ok) return null;
    const body = (await response.json()) as { version?: string };
    return body.version ?? null;
  } catch {
    return null;
  }
}
