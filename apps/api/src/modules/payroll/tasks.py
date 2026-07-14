"""Payroll Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="payroll.payroll_run_scheduler")
def payroll_run_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollPeriod

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollPeriod).where(
                    PayPayrollPeriod.is_deleted.is_(False),
                    PayPayrollPeriod.status == "open",
                )
            ).all()
        )
        return {"status": "ok", "open_periods": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.payslip_generation")
def payslip_generation() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollRun

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollRun).where(
                    PayPayrollRun.is_deleted.is_(False),
                    PayPayrollRun.status == "approved",
                )
            ).all()
        )
        return {"status": "ok", "approved_runs": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.loan_installment_processor")
def loan_installment_processor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayLoanInstallment

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayLoanInstallment).where(
                    PayLoanInstallment.is_deleted.is_(False),
                    PayLoanInstallment.status == "scheduled",
                )
            ).all()
        )
        return {"status": "ok", "due_installments": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.bonus_reminders")
def bonus_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayBonus

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayBonus).where(
                    PayBonus.is_deleted.is_(False),
                    PayBonus.status == "submitted",
                )
            ).all()
        )
        return {"status": "ok", "pending_bonuses": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.payroll_post_retry")
def payroll_post_retry() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollPosting

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollPosting).where(
                    PayPayrollPosting.is_deleted.is_(False),
                    PayPayrollPosting.status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_postings": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.refresh_payroll_summary")
def refresh_payroll_summary() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollSummary

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollSummary).where(
                    PayPayrollSummary.is_deleted.is_(False),
                    PayPayrollSummary.status == "draft",
                )
            ).all()
        )
        return {"status": "ok", "draft_summaries": len(rows)}
    finally:
        db.close()
