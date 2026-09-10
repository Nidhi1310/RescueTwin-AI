# Day 18 — Observability & reliability

Day 18 adds lightweight production observability around the existing RescueTwin AI API.

## Goals

- Give every request a traceable request ID.
- Preserve a caller-supplied `X-Request-ID` when present.
- Measure request duration using a monotonic clock.
- Emit request completion/failure logs through the application logger.
- Add a readiness endpoint for startup health checks.
- Preserve existing API response payloads and decision logic.

## Endpoints

- `GET /api/v1/health` remains the liveness check.
- `GET /api/v1/readiness` reports `ready` after startup initialization completes.

Every response receives an `X-Request-ID` header.

## Scope

This increment is limited to observability and readiness behavior. Flood simulation, prediction, routing, recommendation scoring, explainability, and frontend behavior are unchanged.
