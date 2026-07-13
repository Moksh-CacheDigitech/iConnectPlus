"""Unit tests for journal reversal."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.finance.domain.exceptions import JournalStateError
from modules.finance.service.journal_service import JournalService


def test_reversal_requires_posted_journal() -> None:
    db = MagicMock()
    svc = JournalService(db)
    journal = MagicMock()
    journal.status = "draft"
    journal.company_id = uuid4()
    journal.branch_id = uuid4()
    with patch.object(svc, "get_journal", return_value=journal):
        with pytest.raises(JournalStateError):
            svc.reverse(MagicMock(), uuid4())
