"""Unit tests for recruitment Celery tasks."""

from modules.recruitment import tasks as recruitment_tasks


def test_recruitment_task_names_registered():
    assert recruitment_tasks.interview_reminders.name == "recruitment.interview_reminders"
    assert recruitment_tasks.offer_expiry_notifications.name == "recruitment.offer_expiry_notifications"
    assert recruitment_tasks.background_verification_followups.name == "recruitment.background_verification_followups"
    assert recruitment_tasks.candidate_followup_alerts.name == "recruitment.candidate_followup_alerts"
    assert recruitment_tasks.onboarding_due_alerts.name == "recruitment.onboarding_due_alerts"
    assert recruitment_tasks.retry_hr_handoff.name == "recruitment.retry_hr_handoff"
