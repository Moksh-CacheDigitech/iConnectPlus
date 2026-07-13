"""Sales Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="sales.expire_quotations")
def expire_quotations() -> dict:
    """Mark past-valid_until quotations as expired."""
    return {"status": "stub", "expired": 0}


@celery_app.task(name="sales.recalculate_credit_exposure")
def recalculate_credit_exposure() -> dict:
    """Recalculate credit_used / credit_available from open AR."""
    return {"status": "stub", "updated": 0}


@celery_app.task(name="sales.send_quotation_notifications")
def send_quotation_notifications() -> dict:
    """Notify sales execs of quotations nearing expiry."""
    return {"status": "stub", "sent": 0}


@celery_app.task(name="sales.retry_invoice_posting")
def retry_invoice_posting() -> dict:
    """Retry failed invoice finance postings."""
    return {"status": "stub", "retried": 0}


@celery_app.task(name="sales.sync_invoice_payment_status")
def sync_invoice_payment_status() -> dict:
    """Sync invoice amount_paid / status from AR ledger."""
    return {"status": "stub", "synced": 0}
