"""Procurement Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="procurement.expire_vendor_quotations")
def expire_vendor_quotations() -> dict:
    """Mark past-valid_until vendor quotations as expired."""
    return {"status": "stub", "expired": 0}


@celery_app.task(name="procurement.retry_invoice_posting")
def retry_invoice_posting() -> dict:
    """Retry failed purchase invoice finance postings."""
    return {"status": "stub", "retried": 0}
