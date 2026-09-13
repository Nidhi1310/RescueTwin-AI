# RescueTwin AI — Architecture

## System shape

RescueTwin AI uses a backend-authoritative architecture:

```text
React/Vite Dashboard
        |
        | /api requests
        v
FastAPI API Layer
        |
        v
Decision Engine
   |    |    |    |
   v    v    v    v
Prediction Simulation Routing Recommendations
                         |
                         +-- Hospital
                         +-- Shelter
                         +-- Rescue Team
        |
        v
Report Generation
```

The district profile is static and fictional. Simulation and operational calculations are deterministic so the same scenario and inputs produce reproducible results.

## Frontend

The React/TypeScript frontend presents the operational map, scenario controls, analytics/recommendation panels, and report controls. It requests operational state from the backend rather than maintaining an independent decision model.

The frontend build is managed by Vite and styled with Tailwind CSS. React Leaflet renders the operational map and Recharts is available for dashboard analytics.

## Backend API

FastAPI exposes typed endpoints under `/api/v1`. Pydantic models define the contracts between HTTP handlers and services.

Important routes include:

| Route | Responsibility |
|---|---|
| `GET /health` | service health |
| `GET /district` | district metadata and operational assets |
| `GET /simulate` | scenario simulation |
| `GET /route` | safe-route calculation |
| `GET /recommendations/hospital` | hospital ranking |
| `GET /recommendations/team` | rescue-team ranking |
| `POST /predict` | flood-severity prediction |
| `POST /assess-damage` | uploaded-image assessment |
| `POST /decision-engine` | unified incident decision bundle |
| `POST /generate-report` | deterministic report from a decision bundle |

## District data

The district service supplies the fictional district profile: zones, roads, hospitals, shelters, and rescue teams. Entity IDs are the stable references used by the map, routing layer, recommendations, decision engine, and report.

## Flood simulation

`flood_simulation.py` applies explicit configurations for moderate, severe, and extreme scenarios. Zone severity is derived from elevation and drainage susceptibility plus scenario rainfall intensity. Road closures are derived from adjacent-zone severity thresholds.

The simulation contains no live data dependency, making it repeatable.

## Flood prediction

`flood_prediction.py` loads the persisted XGBoost baseline artifact and predicts a bounded 0–100 flood severity score from:

- rainfall
- elevation
- drainage score
- previous water level

It also returns confidence and an explanation. Training uses deterministic seeds.

## Routing

`routing_service.py` builds an in-memory weighted graph from district roads and virtual links between facilities/teams and their home zones. Dijkstra shortest-path search ignores road IDs blocked by the current flood simulation.

The same scenario therefore determines the road constraints used by operational routing.

## Recommendation services

### Hospital

The hospital service filters candidates by available capacity and flood safety, then evaluates reachable candidates using flood safety, capacity, and safe-route distance.

### Shelter

The shelter service applies capacity, flood-risk, and safe-route constraints, then ranks remaining shelters using explicit suitability factors.

### Rescue team

The team allocation service considers availability, specialty matching when requested, travel distance, and personnel availability. Results include ranking and reasoning factors.

## Decision engine

`decision_engine.py` is the orchestration layer. It:

1. validates environmental inputs through typed models;
2. obtains the ML flood prediction;
3. resolves the selected scenario;
4. runs the flood simulation;
5. derives blocked-road IDs;
6. calculates hospital, shelter, and rescue-team recommendations;
7. calculates safe routes for selected operational resources;
8. optionally performs image damage assessment;
9. returns one `DecisionEngineResponse`.

An explicit UI scenario is passed as `scenario_override`, making the selected scenario the source of truth for the operational simulation.

## Report generation

`report_generation.py` consumes the complete decision response rather than recomputing operational decisions. The report therefore reflects the incident zone, scenario, severity, blocked roads, and selected recommendations from the same decision bundle.

## Request flow

```text
Scenario selected
      |
      v
GET /simulate --------------------+
      |                           |
      v                           |
Map shows scenario state          |
                                  |
Incident zone selected            |
      |                           |
      v                           |
POST /decision-engine <-----------+
      |
      +--> flood prediction
      +--> same scenario simulation
      +--> blocked roads
      +--> safe routes
      +--> hospital recommendation
      +--> shelter recommendation
      +--> rescue team allocation
      +--> optional damage assessment
      |
      v
Decision bundle
      |
      v
POST /generate-report
      |
      v
Incident report
```

## Testing boundary

The `tests/` directory exercises service behavior and API contracts, including regression coverage and the scenario-to-report integration path. See [DEMO.md](DEMO.md) for the operator workflow and [README.md](../README.md) for commands.
