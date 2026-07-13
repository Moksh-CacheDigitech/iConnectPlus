"""Inventory security / permission constant tests."""

from modules.inventory.permissions import (
    INV_PERMISSIONS,
    INVENTORY_CONTROLLER_PERMISSIONS,
    WAREHOUSE_EXECUTIVE_PERMISSIONS,
    WAREHOUSE_MANAGER_PERMISSIONS,
)


def test_inventory_permissions_are_unique():
    codes = [p[0] for p in INV_PERMISSIONS]
    assert len(codes) == len(set(codes))
    assert all(":" in c for c in codes)
    assert all(p[3] == "inventory" for p in INV_PERMISSIONS)


def test_role_bundles_subset_of_permissions():
    all_codes = {p[0] for p in INV_PERMISSIONS}
    for code in WAREHOUSE_EXECUTIVE_PERMISSIONS:
        assert code in all_codes
    for code in WAREHOUSE_MANAGER_PERMISSIONS:
        assert code in all_codes
    for code in INVENTORY_CONTROLLER_PERMISSIONS:
        assert code in all_codes


def test_controller_superset_of_manager():
    assert set(WAREHOUSE_MANAGER_PERMISSIONS).issubset(set(INVENTORY_CONTROLLER_PERMISSIONS))
    assert "inventory.adjustment:post" in INVENTORY_CONTROLLER_PERMISSIONS
    assert "inventory.valuation:run" in INVENTORY_CONTROLLER_PERMISSIONS
