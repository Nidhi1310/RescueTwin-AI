import type { DistrictProfile } from "./types";

const DISTRICT_ENDPOINT = "/api/v1/district";

export async function fetchDistrict(): Promise<DistrictProfile> {
  const response = await fetch(DISTRICT_ENDPOINT);
  if (!response.ok) {
    throw new Error(`District data request failed (${response.status}).`);
  }
  return (await response.json()) as DistrictProfile;
}
