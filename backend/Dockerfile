FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    RESCUETWIN_DATASET_PATH=/app/data/flood_training.csv \
    RESCUETWIN_ARTIFACT_PATH=/app/artifacts/flood_severity_xgb.json

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY ai ./ai
COPY data ./data

# Train at build time so the model artifact always matches the installed XGBoost version.
RUN python ai/train_flood_model.py

# Run as an unprivileged user.
RUN useradd --system --uid 10001 --no-create-home rescuetwin && chown -R rescuetwin /app
USER rescuetwin

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/v1/health' % os.getenv('PORT','8000'), timeout=4)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
