"""Recruitment Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="recruitment.interview_reminders")
def interview_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecInterview

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecInterview).where(
                    RecInterview.is_deleted.is_(False),
                    RecInterview.status == "scheduled",
                )
            ).all()
        )
        return {"status": "ok", "scheduled_interviews": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.offer_expiry_notifications")
def offer_expiry_notifications() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecOffer

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecOffer).where(
                    RecOffer.is_deleted.is_(False),
                    RecOffer.status == "sent",
                )
            ).all()
        )
        return {"status": "ok", "sent_offers": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.background_verification_followups")
def background_verification_followups() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecBackgroundVerification

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecBackgroundVerification).where(
                    RecBackgroundVerification.is_deleted.is_(False),
                    RecBackgroundVerification.status == "in_progress",
                )
            ).all()
        )
        return {"status": "ok", "in_progress_bgv": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.candidate_followup_alerts")
def candidate_followup_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecCandidate

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecCandidate).where(
                    RecCandidate.is_deleted.is_(False),
                    RecCandidate.status.in_(["applied", "screening", "interview"]),
                )
            ).all()
        )
        return {"status": "ok", "active_candidates": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.onboarding_due_alerts")
def onboarding_due_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecOnboarding

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecOnboarding).where(
                    RecOnboarding.is_deleted.is_(False),
                    RecOnboarding.status == "in_progress",
                )
            ).all()
        )
        return {"status": "ok", "in_progress_onboarding": len(rows)}
    finally:
        db.close()


@celery_app.task(name="recruitment.retry_hr_handoff")
def retry_hr_handoff() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.recruitment.models import RecOnboarding

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(RecOnboarding).where(
                    RecOnboarding.is_deleted.is_(False),
                    RecOnboarding.payroll_handoff_status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_handoffs": len(rows)}
    finally:
        db.close()
