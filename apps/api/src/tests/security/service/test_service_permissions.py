"""Service RBAC permission tests."""

from modules.service.permissions import (
    SERVICE_ADMIN_PERMISSIONS,
    SERVICE_COORDINATOR_PERMISSIONS,
    SERVICE_ENGINEER_PERMISSIONS,
    SERVICE_MANAGER_PERMISSIONS,
    SERVICE_PERMISSIONS,
)


def test_service_permissions_defined():
    assert len(SERVICE_PERMISSIONS) >= 40
    assert "service.request:approve" in [p[0] for p in SERVICE_PERMISSIONS]
    assert "service.expense:post" in [p[0] for p in SERVICE_PERMISSIONS]


def test_service_roles():
    assert SERVICE_MANAGER_PERMISSIONS
    assert SERVICE_ENGINEER_PERMISSIONS
    assert SERVICE_COORDINATOR_PERMISSIONS
    assert SERVICE_ADMIN_PERMISSIONS
    assert "service.request:approve" in SERVICE_MANAGER_PERMISSIONS
    assert "service.expense:post" in SERVICE_ADMIN_PERMISSIONS
