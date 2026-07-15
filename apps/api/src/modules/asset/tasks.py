"""Asset Celery task stubs per ERD_15 section 15."""

from workers.celery_app import celery_app


@celery_app.task(name="asset.maintenance_due_alerts")
def maintenance_due_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetMaintenancePlan

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetMaintenancePlan).where(
                    AstAssetMaintenancePlan.is_deleted.is_(False),
                    AstAssetMaintenancePlan.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_plans": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.warranty_expiry_alerts")
def warranty_expiry_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetWarranty

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetWarranty).where(
                    AstAssetWarranty.is_deleted.is_(False),
                    AstAssetWarranty.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_warranties": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.insurance_expiry_alerts")
def insurance_expiry_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetInsurance

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetInsurance).where(
                    AstAssetInsurance.is_deleted.is_(False),
                    AstAssetInsurance.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_insurances": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.depreciation_scheduler")
def depreciation_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetDepreciation

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetDepreciation).where(
                    AstAssetDepreciation.is_deleted.is_(False),
                    AstAssetDepreciation.status == "draft",
                )
            ).all()
        )
        return {"status": "ok", "draft_depreciations": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.asset_audit_reminders")
def asset_audit_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetAudit

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetAudit).where(
                    AstAssetAudit.is_deleted.is_(False),
                    AstAssetAudit.status == "planned",
                )
            ).all()
        )
        return {"status": "ok", "planned_audits": len(rows)}
    finally:
        db.close()


@celery_app.task(name="asset.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.asset.models import AstAssetDepreciation

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(AstAssetDepreciation).where(
                    AstAssetDepreciation.is_deleted.is_(False),
                    AstAssetDepreciation.status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_depreciations": len(rows)}
    finally:
        db.close()
