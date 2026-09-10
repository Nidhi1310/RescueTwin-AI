# RescueTwin AI Release Checklist

## Runtime

- [ ] Backend starts on port 8000.
- [ ] Frontend starts with Vite.
- [ ] `/api/v1/health` returns `ok`.
- [ ] District metadata loads.

## Core workflow

- [ ] Moderate, Severe, and Extreme scenarios load.
- [ ] Flooded zones and blocked roads update with the scenario.
- [ ] Incident zone selection triggers one decision bundle.
- [ ] Safe routes avoid blocked roads.
- [ ] Hospital recommendation is populated or clearly reports no suitable hospital.
- [ ] Shelter recommendation is populated or clearly reports no suitable shelter.
- [ ] Rescue team allocation is populated or clearly reports no suitable team.
- [ ] Each selected recommendation shows a human-readable explanation and score factors.
- [ ] Incident report generates successfully.
- [ ] Report can be copied and downloaded as text.
- [ ] Analytics and operations summary match the active incident/scenario.

## Quality

- [ ] Backend test suite passes locally.
- [ ] Frontend TypeScript/build check passes locally.
- [ ] Docker Compose builds and starts both services.
- [ ] No secrets or local environment files are committed.
- [ ] README setup and demo flow are current.

## Portfolio demo

- [ ] Demonstrate a moderate scenario first.
- [ ] Switch to extreme to show blocked-road and severity changes.
- [ ] Select an incident and explain why the selected hospital, shelter, and team won their scores.
- [ ] Generate the report and show export actions.
- [ ] Show analytics as the final system overview.
