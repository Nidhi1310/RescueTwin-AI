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
