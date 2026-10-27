# Review fixes

Every issue from the project review and where it was fixed. Regression tests: `tests/test_review_fixes.py`.

| Issue | Fix |
|---|---|
| Worst-hit zones got no team/hospital/shelter, no fallback | `incident_isolated` flag + informational boat/air `fallback` options on all three recommenders; warnings and report sections |
| Routing race condition (global graph rebuilt per call) | Immutable cached `RoutingGraph`; recommenders no longer rebuild; atomic default swap |
| `_build_route` always "success"; same-point route = "no route" | Real `no_route_available` status; self-route is a valid 0 km route |
| Parallel roads overwritten | Adjacency list keeps every edge |
| ML output unused | Drives `priority` and severity-weighted team/hospital scoring |
| Confidence always "high" | Derived from holdout skill **and** input support; adds `expected_error_points`, `out_of_support_inputs`, `model_basis` |
| UI showed the simulation score as the "prediction" | Headline is the ML score; simulation shown separately |
| Contradictory / fabricated inputs, "real-time metrics" claim | Server resolves inputs; contradictions → 422; presets disclosed in `warnings`; report wording corrected |
| Hash-based fake damage "AI" with fake confidence | Real image decoding + colour-coverage heuristic; no fabricated confidence; honest disclaimer |
| Bad image silently dropped | Explicit warning in the bundle; UI now uploads images |
| Non-images accepted via extension/magic bytes | Full decode and format allow-list; pixel and size limits |
| Specialty not a constraint; case-sensitive | Hard constraint, normalised, unknown values → 422 with options |
| Same team assigned to every incident | `dispatch_ledger` + `commit` / `DELETE /dispatch/{zone}` |
| Capacity ignored; hospital `services` unused | Capacity-gap warning; `required_service` hard filter |
| Distance only 20% of hospital score | Severity-scaled weight (10–30%) |
| Shelter explanation described the wrong shelter | Explanation computed from the selected shelter |
| Forged reports | HMAC-signed bundles; `/generate-report` verifies |
| Report indentation / markdown bug, `.txt` download | Rebuilt report; `.md` download |
| No upload cap | 8 MB cap (413) + early Content-Length rejection; nginx limit |
| No auth / rate limit / audit | Optional `X-API-Key`, sliding-window limiter, audit logger |
| CORS `*` on Render | Per-deploy value (`sync: false`), startup warning, narrower methods/headers |
| Pickle model + version warning | XGBoost-native JSON + SHA-256 metadata; verified at startup |
| Unpinned dependencies | Pinned backend and frontend; dev deps split out |
| Training path hardcoded to `/app` | Repo-relative defaults + env overrides; CI runs the training command |
| Root containers, no healthchecks | Non-root images, health checks, `depends_on: service_healthy` |
| Frontend report-race | Request-id guard; aborts on selection change |
| Repo clutter | Patches archived; empty placeholder dirs removed; README corrected |

## Not fixable in code (documented instead)

- The ML model is trained on a formula-derived synthetic label; it cannot demonstrate real skill without real data.
- Team reservations are per-process; multi-worker deployments need a shared store.
- A static SPA cannot hold an API secret; use an authenticating gateway for real deployments.
- Render's free tier sleeps when idle.
