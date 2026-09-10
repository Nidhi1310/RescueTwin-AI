from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_returned_and_preserved() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/health",
            headers={"X-Request-ID": "test-request-123"},
        )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_request_id_is_generated_when_missing() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert len(request_id) == 32


def test_readiness_endpoint_reports_ready() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_observability_does_not_change_health_payload() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.json() == {
        "status": "ok",
        "service": "rescuetwin-api",
    }
