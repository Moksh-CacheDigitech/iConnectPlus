"""Security tests for Integration Hub permissions."""

from modules.integration.permissions import (
    API_MANAGER_PERMISSIONS,
    INTEGRATION_ADMIN_PERMISSIONS,
    INTEGRATION_ENGINEER_PERMISSIONS,
    INTEGRATION_PERMISSIONS,
    SYSTEM_OPERATOR_PERMISSIONS,
)


def test_integration_permissions_defined():
    codes = [p[0] for p in INTEGRATION_PERMISSIONS]
    assert "integration.connector:approve" in codes
    assert "integration.sync:run" in codes
    assert "integration.dlq:reprocess" in codes


def test_integration_roles():
    assert len(INTEGRATION_ADMIN_PERMISSIONS) == len(INTEGRATION_PERMISSIONS)
    assert any("connector" in p for p in INTEGRATION_ENGINEER_PERMISSIONS)
    assert any("credential" in p for p in API_MANAGER_PERMISSIONS)
    assert any("dlq" in p for p in SYSTEM_OPERATOR_PERMISSIONS)
