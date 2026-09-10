# Day 24 — Dockerization

## Goal
Provide a simple reproducible containerized option while preserving the existing local development workflow.

## Containers
- `backend/Dockerfile` builds the FastAPI service and serves it on port 8000.
- `frontend/Dockerfile` builds the React/Vite application and serves the production bundle through Nginx on port 80.
- `frontend/nginx.conf` enables SPA fallback routing.
- `docker-compose.yml` provides a minimal two-service setup.

## Container workflow

From the repository root:

```powershell
docker compose build
docker compose up
```

Then open the frontend at `http://localhost:5173` and the backend at `http://localhost:8000`.

To stop the stack:

```powershell
docker compose down
```

## Local workflow
The existing Python/Uvicorn backend and Vite frontend commands remain the primary development path. Docker is an optional reproducibility and handoff path.

## Verification
Run the Docker build and compose stack locally when Docker Desktop is available. Also run the existing backend tests and frontend production build to ensure the non-container workflow remains intact.
