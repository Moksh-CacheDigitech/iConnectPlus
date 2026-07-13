"""Procurement Celery task smoke tests."""

from modules.procurement.tasks import expire_vendor_quotations, retry_invoice_posting


def test_expire_vendor_quotations_stub() -> None:
    result = expire_vendor_quotations()
    assert result["status"] == "stub"
    assert result["expired"] == 0


def test_retry_invoice_posting_stub() -> None:
    result = retry_invoice_posting()
    assert result["status"] == "stub"
    assert result["retried"] == 0
