# RescueTwin AI Data Dictionary

## Fictional district

The application models one fictional flood-prone district with zones, roads, hospitals, shelters, and rescue teams. The dataset is deterministic so the same scenario produces the same operational result.

## Zones

- `id`: stable zone identifier.
- `elevation_m`: elevation used by flood simulation and prediction.
- `drainage_score`: local drainage quality on a 0–10 scale.
- `population`: exposed population estimate.
- `vulnerability_notes`: qualitative context shown in the map.

## Roads

Roads connect zones and contain a length and geometry. Flood simulation marks roads as blocked; the routing engine excludes those road IDs when calculating safe paths.

## Facilities

Hospitals and shelters expose capacity and current occupancy. Recommendation engines calculate available capacity and combine it with flood safety and route distance.

## Rescue teams

Teams expose availability status, personnel count, home zone, and specialties. Allocation considers safe-route distance, specialty match, and personnel availability.

## Recommendation reasoning

Hospital, shelter, and team candidates expose `reasoning_factors`. Each factor has a human-readable value, a normalized weight, and a numeric contribution. Contributions add up to the candidate suitability score, making the ranking inspectable rather than opaque.
