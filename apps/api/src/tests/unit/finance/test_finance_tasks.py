"""Finance Celery task tests."""

from unittest.mock import MagicMock, patch

from modules.finance.tasks import (
    compute_aging_buckets,
    period_close_reminder,
    process_recurring_journals,
    sync_currency_rates,
)


def test_recurring_journals_stub() -> None:
    result = process_recurring_journals()
    assert result["status"] == "stub"


def test_sync_currency_rates_stub() -> None:
    result = sync_currency_rates()
    assert result["status"] == "stub"


def test_period_close_reminder_stub() -> None:
    result = period_close_reminder()
    assert result["status"] == "stub"


def test_compute_aging_buckets_runs() -> None:
    mock_db = MagicMock()
    mock_db.scalars.return_value.all.return_value = []
    with patch("modules.finance.tasks.SessionLocal", return_value=mock_db):
        result = compute_aging_buckets()
    assert result["status"] == "ok"
