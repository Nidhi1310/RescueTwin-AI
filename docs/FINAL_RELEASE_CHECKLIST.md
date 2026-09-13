# RescueTwin AI — Final Release Checklist

## Verification
- Backend regression suite: 50 tests expected to pass.
- Frontend production build: `npm.cmd run build`.
- Main demo flow: choose Moderate/Severe/Extreme scenario → select incident zone → run Decision Engine → review map and recommendations → generate/download incident report.
- Confirm the same incident zone and scenario remain consistent across map, recommendations, analytics, and report.
- Confirm report generation and download work without exposing raw errors.

## Release Hygiene
- Keep the fictional district deterministic and internally consistent.
- Keep generated/build artifacts out of version control unless intentionally required.
- Do not add new functionality during release preparation.
- Review console/network errors during the demo and resolve only release-blocking issues.

## Portfolio Demo
1. Start the backend.
2. Start the frontend.
3. Open the dashboard.
4. Select a flood scenario.
5. Select a flood zone.
6. Review prediction, rescue-team, hospital, and shelter recommendations.
7. Inspect the operational map and route.
8. Generate the incident report.
9. Download the report and verify that it matches the selected incident.

## Release Decision
Ship when backend tests pass, the frontend build passes, the complete scenario-to-report workflow is verified, and the documentation in `docs/` and `README.md` is sufficient for a new engineer to run the project.
