"""Project RBAC permission tests."""

from modules.project.permissions import (
    PROJECT_ADMIN_PERMISSIONS,
    PROJECT_COORDINATOR_PERMISSIONS,
    PROJECT_MANAGER_PERMISSIONS,
    PROJECT_MEMBER_PERMISSIONS,
    PROJECT_PERMISSIONS,
)


def test_project_permissions_defined():
    assert len(PROJECT_PERMISSIONS) >= 40
    assert "project.project:close" in [p[0] for p in PROJECT_PERMISSIONS]
    assert "project.cost:post" in [p[0] for p in PROJECT_PERMISSIONS]


def test_project_roles():
    assert PROJECT_MEMBER_PERMISSIONS
    assert PROJECT_COORDINATOR_PERMISSIONS
    assert PROJECT_MANAGER_PERMISSIONS
    assert PROJECT_ADMIN_PERMISSIONS
    assert "project.project:approve" in PROJECT_MANAGER_PERMISSIONS
    assert "project.cost:post" in PROJECT_ADMIN_PERMISSIONS
