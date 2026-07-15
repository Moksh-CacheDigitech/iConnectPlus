"""Service Celery task stubs per ERD_16 section 15."""

from workers.celery_app import celery_app


@celery_app.task(name="service.sla_breach_monitor")
def sla_breach_monitor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceRequest

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceRequest).where(
                    SvcServiceRequest.is_deleted.is_(False),
                    SvcServiceRequest.sla_status.in_(["at_risk", "breached"]),
                )
            ).all()
        )
        return {"status": "ok", "at_risk_or_breached": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.work_order_reminders")
def work_order_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceWorkOrder

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceWorkOrder).where(
                    SvcServiceWorkOrder.is_deleted.is_(False),
                    SvcServiceWorkOrder.status.in_(["approved", "assigned", "in_progress"]),
                )
            ).all()
        )
        return {"status": "ok", "open_work_orders": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.preventive_service_scheduler")
def preventive_service_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceContract

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceContract).where(
                    SvcServiceContract.is_deleted.is_(False),
                    SvcServiceContract.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_contracts": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.service_contract_expiry")
def service_contract_expiry() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceContract

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceContract).where(
                    SvcServiceContract.is_deleted.is_(False),
                    SvcServiceContract.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "contracts_to_review": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.customer_feedback_reminders")
def customer_feedback_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceResolution

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceResolution).where(
                    SvcServiceResolution.is_deleted.is_(False),
                    SvcServiceResolution.status == "completed",
                )
            ).all()
        )
        return {"status": "ok", "completed_resolutions": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceExpense

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceExpense).where(
                    SvcServiceExpense.is_deleted.is_(False),
                    SvcServiceExpense.status == "approved",
                    SvcServiceExpense.finance_journal_id.is_(None),
                )
            ).all()
        )
        return {"status": "ok", "unposted_expenses": len(rows)}
    finally:
        db.close()
