from fastapi.testclient import TestClient

from app.main import app


def test_liveness() -> None:
    with TestClient(app) as client:
        res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_readiness_reports_each_dependency() -> None:
    # No Mongo/Redis in unit tests, so this should report "degraded" without crashing.
    with TestClient(app) as client:
        res = client.get("/health/ready")
    body = res.json()
    assert set(body["checks"]) == {"mongo", "redis"}
    assert res.status_code in (200, 503)
