"""Project Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="project.deadline_reminders")
def deadline_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectTask

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectTask).where(
                    PrjProjectTask.is_deleted.is_(False),
                    PrjProjectTask.status.in_(["open", "in_progress"]),
                )
            ).all()
        )
        return {"status": "ok", "open_tasks": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.timesheet_reminders")
def timesheet_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjTimesheet

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjTimesheet).where(
                    PrjTimesheet.is_deleted.is_(False),
                    PrjTimesheet.status == "draft",
                )
            ).all()
        )
        return {"status": "ok", "draft_timesheets": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.budget_threshold_alerts")
def budget_threshold_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectBudget

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectBudget).where(
                    PrjProjectBudget.is_deleted.is_(False),
                    PrjProjectBudget.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_budgets": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.risk_review_notifications")
def risk_review_notifications() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectRisk

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectRisk).where(
                    PrjProjectRisk.is_deleted.is_(False),
                    PrjProjectRisk.status.in_(["identified", "mitigating"]),
                )
            ).all()
        )
        return {"status": "ok", "open_risks": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.project_health_refresh")
def project_health_refresh() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProject

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProject).where(
                    PrjProject.is_deleted.is_(False),
                    PrjProject.status == "in_progress",
                )
            ).all()
        )
        return {"status": "ok", "in_progress_projects": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectCost

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectCost).where(
                    PrjProjectCost.is_deleted.is_(False),
                    PrjProjectCost.status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_costs": len(rows)}
    finally:
        db.close()
