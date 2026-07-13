"""Integration tests for organization routing."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_organization_routes_registered() -> None:
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    assert "/api/v1/companies" in paths
    assert "/api/v1/branches" in paths
    assert "/api/v1/departments" in paths
    assert "/api/v1/business-units" in paths
    assert "/api/v1/locations" in paths
    assert "/api/v1/cost-centers" in paths
    assert "/api/v1/profit-centers" in paths
    assert "/api/v1/organization/tree" in paths
    assert "/api/v1/auth/context" in paths
