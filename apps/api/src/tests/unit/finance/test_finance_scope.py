"""Finance scope isolation tests."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.exceptions import ForbiddenException
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext


def test_company_isolation() -> None:
    db = MagicMock()
    validator = FinanceScopeValidator(db)
    ctx = TenantContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        user_type="employee",
        company_id=uuid4(),
    )
    other_company = uuid4()
    with pytest.raises(ForbiddenException):
        validator.validate_company_access(ctx, other_company)


def test_branch_isolation() -> None:
    db = MagicMock()
    validator = FinanceScopeValidator(db)
    ctx = TenantContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        user_type="employee",
        company_id=uuid4(),
        branch_id=uuid4(),
    )
    other_branch = uuid4()
    with pytest.raises(ForbiddenException):
        validator.validate_branch_access(ctx, other_branch)
