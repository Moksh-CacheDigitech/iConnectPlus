"""Unit tests for master data scope validation."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.master_scope_validator import MasterScopeValidator


def test_master_scope_requires_company_context() -> None:
    db = MagicMock()
    ctx = TenantContext(
        tenant_id=uuid4(),
        user_id=uuid4(),
        user_type="employee",
        company_id=None,
    )
    validator = MasterScopeValidator(db)
    with pytest.raises(ForbiddenException):
        validator.resolve_company_id(ctx, None)
