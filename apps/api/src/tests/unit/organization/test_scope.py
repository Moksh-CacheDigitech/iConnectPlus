"""Company isolation unit tests."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.service.org_scope_validator import OrgScopeValidator


def test_scope_denied_for_unassigned_company() -> None:
    db = MagicMock()
    db.scalar.return_value = None
    ctx = TenantContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        user_type="employee",
        company_id=uuid4(),
    )
    validator = OrgScopeValidator(db)
    with pytest.raises(ForbiddenException):
        validator.validate_company_access(ctx, uuid4())
