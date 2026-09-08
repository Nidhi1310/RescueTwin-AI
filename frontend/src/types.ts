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
  predicted_flood_severity: number;
  confidence: "low" | "medium" | "high";
}

export interface RecommendationCandidate {
  hospital_id?: string;
  hospital_name?: string;
  shelter_id?: string;
  shelter_name?: string;
  team_id?: string;
  team_name?: string;
  zone_id?: string;
  home_zone_id?: string;
  route_distance_km: number;
  estimated_travel_time_minutes: number;
  available_capacity?: number;
  personnel_count?: number;
  flood_risk_score?: number;
  suitability_score: number;
  rationale: string;
  specialties?: string[];
  specialty_match?: boolean;
}

export interface HospitalRecommendationResponse {
  status: string;
  start_id: string;
  scenario: string;
  selected_hospital: RecommendationCandidate | null;
  ranked_hospitals: RecommendationCandidate[];
  excluded_hospitals: { hospital_id: string; hospital_name: string; reason: string }[];
  explanation: string;
}

export interface ShelterRecommendationResponse {
  status: string;
  start_id: string;
  scenario: string;
  selected_shelter: RecommendationCandidate | null;
  ranked_shelters: RecommendationCandidate[];
  excluded_shelters: { shelter_id: string; shelter_name: string; reason: string }[];
  explanation: string;
}

export interface TeamAllocationResponse {
  status: string;
  incident_zone_id: string;
  scenario: string;
  required_specialty: string | null;
  selected_team: RecommendationCandidate | null;
  ranked_teams: RecommendationCandidate[];
  excluded_teams: { team_id: string; team_name: string; reason: string }[];
  explanation: string;
}

export interface DamageAssessmentResponse {
  [key: string]: unknown;
}

export interface DecisionEngineResponse {
  incident_zone_id: string;
  prediction: FloodPredictionResponse;
  simulation: FloodSimulationResult;
  damage_assessment: DamageAssessmentResponse | null;
  hospital_recommendation: HospitalRecommendationResponse;
  hospital_route: RouteResponse | null;
  shelter_recommendation: ShelterRecommendationResponse;
  shelter_route: RouteResponse | null;
  team_allocation: TeamAllocationResponse;
  team_route: RouteResponse | null;
}

export interface IncidentReportResponse {
  report_content: string;
  generated_at: string;
}
