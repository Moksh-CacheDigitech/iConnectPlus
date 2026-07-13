"""Security tests for finance RBAC and segregation of duties."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.finance.domain.exceptions import SegregationOfDutiesError
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext


def test_creator_cannot_approve_journal() -> None:
    db = MagicMock()
    svc = JournalService(db)
    user_id = uuid4()
    ctx = TenantContext(
        tenant_id=uuid4(),
        user_id=user_id,
        user_type="employee",
        company_id=uuid4(),
        branch_id=uuid4(),
    )
    journal = MagicMock()
    journal.created_by = user_id
    journal.workflow_instance_id = uuid4()
    journal.status = "submitted"
    with patch.object(svc, "get_journal", return_value=journal):
        with pytest.raises(SegregationOfDutiesError):
            svc.approve(ctx, uuid4())


def test_creator_cannot_post_journal() -> None:
    db = MagicMock()
    svc = PostingService(db)
    user_id = uuid4()
    ctx = TenantContext(
        tenant_id=uuid4(),
        user_id=user_id,
        user_type="employee",
        company_id=uuid4(),
        branch_id=uuid4(),
    )
    journal = MagicMock()
    journal.created_by = user_id
    journal.period_id = uuid4()
    with patch.object(svc._journal_svc, "get_journal", return_value=journal):
        with pytest.raises(SegregationOfDutiesError):
            svc.post_journal(ctx, uuid4())
