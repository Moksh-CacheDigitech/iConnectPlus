"""Security tests for E-Commerce permissions."""

from modules.ecommerce.permissions import (
    ECOMMERCE_ADMIN_PERMISSIONS,
    ECOMMERCE_MANAGER_PERMISSIONS,
    ECOMMERCE_PERMISSIONS,
    MARKETPLACE_MANAGER_PERMISSIONS,
    STORE_OPERATOR_PERMISSIONS,
)


def test_ecommerce_permissions_defined():
    codes = [p[0] for p in ECOMMERCE_PERMISSIONS]
    assert "ecommerce.store:approve" in codes
    assert "ecommerce.order:accept" in codes
    assert "ecommerce.marketplace:sync" in codes


def test_ecommerce_roles():
    assert len(ECOMMERCE_ADMIN_PERMISSIONS) == len(ECOMMERCE_PERMISSIONS)
    assert any("listing" in p for p in ECOMMERCE_MANAGER_PERMISSIONS)
    assert any("marketplace" in p for p in MARKETPLACE_MANAGER_PERMISSIONS)
    assert any("order" in p for p in STORE_OPERATOR_PERMISSIONS)
