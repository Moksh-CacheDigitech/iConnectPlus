"""Unit tests for organization domain enums."""

from modules.organization.domain.enums import OrgStatus


def test_org_status_values() -> None:
    assert OrgStatus.ACTIVE.value == "active"
    assert OrgStatus.DRAFT.value == "draft"
