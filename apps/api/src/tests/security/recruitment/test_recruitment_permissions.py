"""Recruitment RBAC permission tests."""

from modules.recruitment.permissions import (
    HIRING_MANAGER_PERMISSIONS,
    HR_ONBOARDING_PERMISSIONS,
    RECRUITER_PERMISSIONS,
    RECRUITMENT_MANAGER_PERMISSIONS,
    RECRUITMENT_PERMISSIONS,
)


def test_recruitment_permissions_defined():
    assert len(RECRUITMENT_PERMISSIONS) >= 40
    assert "recruitment.onboarding:complete" in [p[0] for p in RECRUITMENT_PERMISSIONS]


def test_recruitment_roles():
    assert RECRUITER_PERMISSIONS
    assert RECRUITMENT_MANAGER_PERMISSIONS
    assert HR_ONBOARDING_PERMISSIONS
    assert HIRING_MANAGER_PERMISSIONS
    assert "recruitment.requisition:approve" in RECRUITMENT_MANAGER_PERMISSIONS
