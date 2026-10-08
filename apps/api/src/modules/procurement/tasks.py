"""Procurement Celery tasks."""

from modules.platform.celery_idempotent import system_job
from workers.celery_app import celery_app


@celery_app.task(name="procurement.expire_vendor_quotations")
def expire_vendor_quotations() -> dict:
    """Mark past-valid_until vendor quotations as expired."""
    return {"status": "stub", "expired": 0}


@celery_app.task(name="procurement.retry_invoice_posting")
def retry_invoice_posting() -> dict:
    """Retry failed purchase invoice finance postings."""
    return {"status": "stub", "retried": 0}


@celery_app.task(name="procurement.inventory_holding_costs")
@system_job("procurement.inventory_holding_costs", window="day")
def inventory_holding_costs() -> dict:
    """Release stock of closed / lost deals and push stock carrying cost into OVF margins."""
    from uuid import uuid4

    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.foundation.domain.value_objects import TenantContext
    from modules.procurement.models.inventory_stock import ProcInventoryStockUnit
    from modules.procurement.service.inventory_ownership_service import InventoryOwnershipService

    db = SessionLocal()
    try:
        tenant_ids = list(
            db.scalars(
                select(ProcInventoryStockUnit.tenant_id)
                .where(ProcInventoryStockUnit.is_deleted.is_(False))
                .distinct()
            ).all()
        )
        system_user = uuid4()
        totals = {"released": 0, "ovfs_priced": 0, "failed_tenants": 0}
        for tenant_id in tenant_ids:
            ctx = TenantContext(tenant_id=tenant_id, user_id=system_user, user_type="super_admin")
            try:
                service = InventoryOwnershipService(db)
                totals["released"] += service.release_closed_deal_stock(ctx)
                totals["ovfs_priced"] += service.push_holding_costs(ctx)
                db.commit()
            except Exception:
                db.rollback()
                totals["failed_tenants"] += 1
        return {"status": "ok", **totals}
    finally:
        db.close()


@celery_app.task(name="procurement.delivery_notifications")
@system_job("procurement.delivery_notifications", window="day")
def delivery_notifications() -> dict:
    """Acknowledge new orders, chase distributors for an ETD, update customers.

    Idempotent: every message is stamped on the PO, so re-running the pass does
    not re-send anything.
    """
    from uuid import uuid4

    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.foundation.domain.value_objects import TenantContext
    from modules.procurement.models.order import ProcOrderHeader
    from modules.procurement.service.scm_delivery_notification_service import (
        ScmDeliveryNotificationService,
    )

    db = SessionLocal()
    try:
        tenant_ids = list(
            db.scalars(
                select(ProcOrderHeader.tenant_id)
                .where(ProcOrderHeader.is_deleted.is_(False))
                .distinct()
            ).all()
        )
        system_user = uuid4()
        totals = {"acknowledged": 0, "etd_chased": 0, "delivery_dates_shared": 0}
        for tenant_id in tenant_ids:
            ctx = TenantContext(
                tenant_id=tenant_id,
                user_id=system_user,
                user_type="super_admin",
            )
            try:
                counts = ScmDeliveryNotificationService(db).run(ctx)
            except Exception:
                db.rollback()
                continue
            db.commit()
            for key, value in counts.items():
                totals[key] += value
        return {"status": "ok", **totals}
    finally:
        db.close()
