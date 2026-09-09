export interface GeoPoint {
  latitude: number;
  longitude: number;
}

export interface FloodZone {
  id: string;
  name: string;
  center: GeoPoint;
  elevation_m: number;
  drainage_score: number;
  population: number;
  vulnerability_notes: string;
}

export interface Facility {
  id: string;
  name: string;
  type: "hospital" | "shelter";
  zone_id: string;
  location: GeoPoint;
  capacity: number;
  current_occupancy: number;
  services: string[];
}

export interface RescueTeam {
  id: string;
  name: string;
  home_zone_id: string;
  location: GeoPoint;
  personnel_count: number;
  specialties: string[];
  status: "available" | "deployed" | "standby";
}

export interface DistrictProfile {
  metadata: {
    id: string;
    name: string;
    region: string;
    country: string;
    timezone: string;
    center: GeoPoint;
    description: string;
  };
  zones: FloodZone[];
  hospitals: Facility[];
  shelters: Facility[];
  rescue_teams: RescueTeam[];
}

export interface RouteResponse {
  status: "success" | "no_route_available";
  distance_km: number;
  path: GeoPoint[];
}

export type RainfallScenario = "moderate" | "severe" | "extreme";

export interface ZoneFloodImpact {
  zone_id: string;
  zone_name: string;
  severity_score: number;
  affected: boolean;
}

export interface BlockedRoad {
  road_id: string;
  road_name: string;
  from_zone_id: string;
  to_zone_id: string;
  reason: string;
}

export interface FloodSimulationResult {
  scenario: RainfallScenario;
  rainfall_intensity: number;
  severity_score: number;
  zone_impacts: ZoneFloodImpact[];
  affected_zones: ZoneFloodImpact[];
  blocked_roads: BlockedRoad[];
  explanation: string;
}

export interface FloodPredictionResponse {
  severity_score: number;
  risk_level: string;
  contributing_factors: Record<string, number>;
  confidence: number;
}

export interface HospitalRecommendationResponse {
  recommended_hospital_id: string;
  hospital_name: string;
  distance_km: number;
  available_capacity: number;
  score: number;
  reasoning: string;
}

export interface ShelterRecommendationResponse {
  recommended_shelter_id: string;
  shelter_name: string;
  distance_km: number;
  available_capacity: number;
  score: number;
  reasoning: string;
}

export interface TeamAllocationResponse {
  assigned_team_id: string;
  team_name: string;
  distance_km: number;
  eta_minutes: number;
  score: number;
  specialty_match: boolean;
  reasoning: string;
}

export interface DecisionEngineResponse {
  incident_zone_id: string;
  prediction: FloodPredictionResponse;
  simulation: FloodSimulationResult;
  damage_assessment: any | null;
  hospital_recommendation: HospitalRecommendationResponse;
  hospital_route: RouteResponse | null;
  shelter_recommendation: ShelterRecommendationResponse;
  shelter_route: RouteResponse | null;
  team_allocation: TeamAllocationResponse;
  team_route: RouteResponse | null;
}

export interface IncidentReportResponse {
  report_markdown: string;
  generated_at: string;
  confidence_level: string;
}
