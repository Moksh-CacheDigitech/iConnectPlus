"""Health endpoint tests."""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_response(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Service health check"
    assert "data" in body
    assert body["data"]["version"] == "0.1.0"
