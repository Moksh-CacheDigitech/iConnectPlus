"""Security tests for HR permissions/roles."""

from modules.hr.permissions import (
    HR_ADMIN_PERMISSIONS,
    HR_EMPLOYEE_PERMISSIONS,
    HR_EXECUTIVE_PERMISSIONS,
    HR_MANAGER_PERMISSIONS,
    HR_PERMISSIONS,
)


def test_permission_codes_unique():
    codes = [p[0] for p in HR_PERMISSIONS]
    assert len(codes) == len(set(codes))
    assert all(c.startswith("hr.") for c in codes)


def test_roles_have_permissions():
    assert "hr.leave:approve" in HR_MANAGER_PERMISSIONS
    assert "hr.leave:approve" not in HR_EMPLOYEE_PERMISSIONS
    assert "hr.employment:create" in HR_EXECUTIVE_PERMISSIONS
    assert len(HR_ADMIN_PERMISSIONS) == len(HR_PERMISSIONS)
