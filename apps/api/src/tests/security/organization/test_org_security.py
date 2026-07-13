"""Security tests for organization APIs."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_companies_requires_auth() -> None:
    response = client.get("/api/v1/companies")
    assert response.status_code == 401


def test_branches_requires_auth() -> None:
    response = client.get("/api/v1/branches")
    assert response.status_code == 401


def test_org_tree_requires_auth() -> None:
    response = client.get("/api/v1/organization/tree")
    assert response.status_code == 401
