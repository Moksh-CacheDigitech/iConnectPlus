"""Inventory Celery tasks."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from workers.celery_app import celery_app

_SYSTEM_USER = UUID("00000000-0000-0000-0000-000000000001")


@celery_app.task(name="inventory.low_stock_alerts")
def low_stock_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.foundation.domain.value_objects import TenantContext
    from modules.inventory.models.reorder_policy import InvReorderPolicy
    from modules.inventory.repository.balance_repository import BalanceRepository

    db = SessionLocal()
    try:
        policies = list(
            db.scalars(
                select(InvReorderPolicy).where(
                    InvReorderPolicy.is_deleted.is_(False),
                    InvReorderPolicy.status == "active",
                )
            ).all()
        )
        alerts = 0
        for policy in policies:
            ctx = TenantContext(
                tenant_id=policy.tenant_id,
                user_id=_SYSTEM_USER,
                company_id=policy.company_id,
                branch_id=None,
                user_type="tenant_admin",
            )
            balances = BalanceRepository(db).list_balances(
                ctx,
                policy.company_id,
                warehouse_id=policy.warehouse_id,
                product_id=policy.product_id,
            )
            for bal in balances:
                if float(bal.available_qty) <= float(policy.reorder_point):
                    alerts += 1
        return {"status": "ok", "alerts": alerts}
    finally:
        db.close()


@celery_app.task(name="inventory.batch_expiry_alerts")
def batch_expiry_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.inventory.models.batch import InvBatch

    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc).date() + timedelta(days=30)
        rows = list(
            db.scalars(
                select(InvBatch).where(
                    InvBatch.is_deleted.is_(False),
                    InvBatch.status == "active",
                    InvBatch.expiry_date.is_not(None),
                    InvBatch.expiry_date <= cutoff,
                )
            ).all()
        )
        return {"status": "ok", "expiring": len(rows)}
    finally:
        db.close()


@celery_app.task(name="inventory.reservation_cleanup")
def reservation_cleanup() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.foundation.domain.value_objects import TenantContext
    from modules.inventory.models.reservation import InvReservation
    from modules.inventory.service.inventory_application_service import (
        InventoryApplicationService,
    )

    db = SessionLocal()
    try:
        older_than = datetime.now(timezone.utc) - timedelta(days=14)
        rows = list(
            db.scalars(
                select(InvReservation).where(
                    InvReservation.is_deleted.is_(False),
                    InvReservation.status.in_(["active", "partially_issued"]),
                    InvReservation.reserved_at.is_not(None),
                    InvReservation.reserved_at < older_than,
                )
            ).all()
        )
        released = 0
        for row in rows:
            ctx = TenantContext(
                tenant_id=row.tenant_id,
                user_id=_SYSTEM_USER,
                company_id=row.company_id,
                branch_id=row.branch_id,
                user_type="tenant_admin",
            )
            InventoryApplicationService(db).release_reservation(ctx, row.id)
            released += 1
        db.commit()
        return {"status": "ok", "released": released}
    finally:
        db.close()


@celery_app.task(name="inventory.recompute_available")
def recompute_available() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.inventory.models.balance import InvStockBalance
    from modules.inventory.service.engines import StockEngine

    db = SessionLocal()
    try:
        engine = StockEngine()
        fixed = 0
        rows = list(
            db.scalars(
                select(InvStockBalance).where(InvStockBalance.is_deleted.is_(False))
            ).all()
        )
        for row in rows:
            expected = float(row.on_hand_qty) - float(row.reserved_qty)
            if abs(float(row.available_qty) - expected) > 0.0001:
                engine.recompute_available(row)
                fixed += 1
        db.commit()
        return {"status": "ok", "fixed": fixed}
    finally:
        db.close()


@celery_app.task(name="inventory.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.inventory.models.adjustment import InvAdjustmentHeader

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(InvAdjustmentHeader).where(
                    InvAdjustmentHeader.is_deleted.is_(False),
                    InvAdjustmentHeader.status == "posted",
                    InvAdjustmentHeader.finance_journal_id.is_(None),
                )
            ).all()
        )
        return {"status": "ok", "pending": len(rows)}
    finally:
        db.close()
