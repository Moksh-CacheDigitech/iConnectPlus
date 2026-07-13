"""Security tests for master data APIs."""

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_employees_requires_auth() -> None:
    assert client.get("/api/v1/employees").status_code == 401


def test_customers_requires_auth() -> None:
    assert client.get("/api/v1/customers").status_code == 401


def test_products_requires_auth() -> None:
    assert client.get("/api/v1/products").status_code == 401


def test_warehouses_requires_auth() -> None:
    assert client.get("/api/v1/warehouses").status_code == 401
