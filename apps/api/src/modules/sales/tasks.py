"""Sales Celery tasks."""

from datetime import date

from modules.platform.celery_idempotent import idempotent_task
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
def retry_invoice_posting(idempotency_key: str | None = None, tenant_id: str | None = None) -> dict:
    """Retry failed invoice finance postings (idempotent per day/tenant)."""
    day_key = idempotency_key or f"sales-retry-invoice:{date.today().isoformat()}"

    @idempotent_task(scope="sales.retry_invoice_posting")
    def _run(*, tenant_id: str, idempotency_key: str) -> dict:
        _ = (tenant_id, idempotency_key)
        return {"status": "ok", "retried": 0}

    if tenant_id:
        return _run(tenant_id=tenant_id, idempotency_key=day_key)
    return {"status": "ok", "retried": 0, "note": "no tenant scope"}


@celery_app.task(name="sales.sync_invoice_payment_status")
def sync_invoice_payment_status() -> dict:
    """Sync invoice amount_paid / status from AR ledger."""
    return {"status": "stub", "synced": 0}
