"""Unit tests for posting engine."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.finance.domain.exceptions import JournalStateError, PostingError
from modules.finance.service.engines.posting_engine import PostingEngine


def test_posting_rejects_non_approved() -> None:
    db = MagicMock()
    engine = PostingEngine(db)
    journal = MagicMock()
    journal.status = "draft"
    journal.id = uuid4()
    with pytest.raises(JournalStateError):
        engine.post_journal(MagicMock(), journal)


def test_posting_rejects_duplicate() -> None:
    db = MagicMock()
    engine = PostingEngine(db)
    journal = MagicMock()
    journal.status = "approved"
    journal.id = uuid4()
    with patch.object(engine._gl, "exists_for_journal", return_value=True):
        with pytest.raises(PostingError):
            engine.post_journal(MagicMock(), journal)
