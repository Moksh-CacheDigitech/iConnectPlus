"""Unit tests for period closing engine."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.finance.domain.exceptions import JournalStateError
from modules.finance.service.engines.period_closing_engine import PeriodClosingEngine


def test_hard_close_requires_flags() -> None:
    db = MagicMock()
    engine = PeriodClosingEngine(db)

    period = MagicMock()
    period.id = uuid4()
    period.status = "open"
    period.ar_closed = False
    period.ap_closed = False
    period.gl_closed = False

    with patch.object(engine._journal, "count_open_journals_in_period", return_value=0):
        with pytest.raises(JournalStateError):
            engine.hard_close(MagicMock(), period)
