"""Asset RBAC permission tests."""

from modules.asset.permissions import (
    ASSET_ADMIN_PERMISSIONS,
    ASSET_AUDITOR_PERMISSIONS,
    ASSET_EXECUTIVE_PERMISSIONS,
    ASSET_MANAGER_PERMISSIONS,
    ASSET_PERMISSIONS,
)


def test_asset_permissions_defined():
    assert len(ASSET_PERMISSIONS) >= 40
    assert "asset.asset:approve" in [p[0] for p in ASSET_PERMISSIONS]
    assert "asset.depreciation:post" in [p[0] for p in ASSET_PERMISSIONS]


def test_asset_roles():
    assert ASSET_EXECUTIVE_PERMISSIONS
    assert ASSET_MANAGER_PERMISSIONS
    assert ASSET_AUDITOR_PERMISSIONS
    assert ASSET_ADMIN_PERMISSIONS
    assert "asset.asset:approve" in ASSET_MANAGER_PERMISSIONS
    assert "asset.depreciation:post" in ASSET_ADMIN_PERMISSIONS
