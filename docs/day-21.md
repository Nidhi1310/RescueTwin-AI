# Day 21 — Backend Testing Pass

## Goal

Expand automated regression coverage across the core RescueTwin AI backend so deterministic simulation, routing, prediction, and incident reporting behavior is protected as the project evolves.

## Coverage added

- Repeated flood simulations return identical results for every rainfall scenario.
- Flood severity and blocked-road counts do not decrease as rainfall severity increases.
- Repeated safe-route calculations return the same path and distance.
- Unknown routing destinations return a controlled `404` response.
- Invalid simulation scenarios return the structured `422` validation response.
- Repeated prediction requests preserve the same response contract and result.
- Generated incident reports preserve the incident zone, predicted severity, confidence, and report heading.

## Verification

Run the complete backend suite from the repository root:

```powershell
$env:PYTHONPATH="backend"
python -m pytest tests -v
```

The Day 21 acceptance target is a clean passing suite. Existing API behavior should remain unchanged; failures should be fixed in the implementation or test assumptions rather than weakening the regression coverage.
