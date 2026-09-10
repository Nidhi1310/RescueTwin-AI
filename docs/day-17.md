# Day 17 — API hardening

Day 17 hardens the existing RescueTwin AI API without changing the decision logic delivered in Day 16.

## Goals

- Reject invalid numeric inputs at the API boundary.
- Return clear 404 responses for unknown operational IDs.
- Return a consistent validation error payload for malformed requests.
- Reject empty uploaded images early.
- Preserve existing response schemas and Day 16 explainability fields.

## Scope

This increment is limited to API validation and error handling. Recommendation scoring, routing algorithms, simulation behavior, and frontend functionality are unchanged.
