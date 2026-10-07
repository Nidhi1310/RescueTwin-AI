#!/usr/bin/env bash
# One-command start for RescueTwin AI (Linux/macOS). Stops stale servers first.
cd "$(dirname "$0")"
for port in 8000 5173; do
  pid=$(lsof -ti tcp:$port 2>/dev/null) && [ -n "$pid" ] && kill $pid 2>/dev/null
done
python3 -m pip install -r backend/requirements-dev.txt
(cd backend && python3 -m uvicorn app.main:app --reload) &
(cd frontend && npm ci && npm run dev) &
echo 'Open http://127.0.0.1:5173 and look for the yellow "BUILD v0.2 · FIXED" badge.'
wait
