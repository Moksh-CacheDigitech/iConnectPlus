"""Manufacturing RBAC permission constants."""

from modules.manufacturing.permissions import (
    MFG_PERMISSIONS,
    PRODUCTION_ENGINEER_PERMISSIONS,
    PRODUCTION_MANAGER_PERMISSIONS,
    PRODUCTION_SUPERVISOR_PERMISSIONS,
    SHOP_FLOOR_OPERATOR_PERMISSIONS,
)


def test_mfg_permissions_non_empty():
    assert len(MFG_PERMISSIONS) >= 30
    codes = {p[0] for p in MFG_PERMISSIONS}
    assert "manufacturing.bom:approve" in codes
    assert "manufacturing.production_order:release" in codes
    assert "manufacturing.scrap:post" in codes


def test_role_permission_lists():
    assert len(SHOP_FLOOR_OPERATOR_PERMISSIONS) > 0
    assert len(PRODUCTION_ENGINEER_PERMISSIONS) >= len(SHOP_FLOOR_OPERATOR_PERMISSIONS)
    assert len(PRODUCTION_SUPERVISOR_PERMISSIONS) >= len(PRODUCTION_ENGINEER_PERMISSIONS)
    assert len(PRODUCTION_MANAGER_PERMISSIONS) >= len(PRODUCTION_SUPERVISOR_PERMISSIONS)
    assert "manufacturing.production_order:release" in PRODUCTION_MANAGER_PERMISSIONS
