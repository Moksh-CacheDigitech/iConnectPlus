"""Unit tests for sales Celery task stubs."""

from modules.sales.tasks import (
    expire_quotations,
    recalculate_credit_exposure,
    retry_invoice_posting,
    send_quotation_notifications,
    sync_invoice_payment_status,
)


def test_expire_quotations_stub() -> None:
    assert expire_quotations()["status"] == "stub"


def test_credit_recalc_stub() -> None:
    assert recalculate_credit_exposure()["updated"] == 0


def test_notification_stub() -> None:
    assert send_quotation_notifications()["sent"] == 0


def test_retry_posting_stub() -> None:
    assert retry_invoice_posting()["retried"] == 0


def test_payment_sync_stub() -> None:
    assert sync_invoice_payment_status()["synced"] == 0
