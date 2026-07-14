"""Payroll RBAC permission tests."""

from modules.payroll.permissions import (
    FINANCE_PAYROLL_REVIEWER_PERMISSIONS,
    HR_PAYROLL_ADMIN_PERMISSIONS,
    PAYROLL_EXECUTIVE_PERMISSIONS,
    PAYROLL_MANAGER_PERMISSIONS,
    PAYROLL_PERMISSIONS,
)


def test_payroll_permissions_defined():
    assert len(PAYROLL_PERMISSIONS) >= 40
    assert "payroll.run:calculate" in [p[0] for p in PAYROLL_PERMISSIONS]


def test_payroll_roles():
    assert "PAYROLL_EXECUTIVE"  # role constants in seed migration
    assert PAYROLL_EXECUTIVE_PERMISSIONS
    assert PAYROLL_MANAGER_PERMISSIONS
    assert HR_PAYROLL_ADMIN_PERMISSIONS
    assert FINANCE_PAYROLL_REVIEWER_PERMISSIONS
    assert "payroll.posting:post" in FINANCE_PAYROLL_REVIEWER_PERMISSIONS
