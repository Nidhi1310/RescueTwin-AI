# Day 19 — Frontend interaction quality

## Goal

Improve the dashboard interaction model around scenario selection, incident selection, loading states, errors, and recommendation rendering.

## Changes

- Centralized frontend API error parsing through `ApiError`.
- Surface backend error messages instead of generic HTTP errors.
- Added explicit simulation, decision, and report error states.
- Added retry actions for failed decision analysis and report generation.
- Clear the selected incident when switching rainfall scenarios so stale recommendations cannot remain attached to the new scenario.
- Preserve the existing decision payload and recommendation rendering behavior on successful requests.

## Verification

Run the frontend production build with:

```powershell
cd frontend
npm.cmd run build
```

Run the backend regression suite with:

```powershell
$env:PYTHONPATH="backend"
python -m pytest tests -v
```
