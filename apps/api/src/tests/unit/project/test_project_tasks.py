"""Unit tests for project Celery tasks."""

from modules.project import tasks as project_tasks


def test_project_task_names_registered():
    assert project_tasks.deadline_reminders.name == "project.deadline_reminders"
    assert project_tasks.timesheet_reminders.name == "project.timesheet_reminders"
    assert project_tasks.budget_threshold_alerts.name == "project.budget_threshold_alerts"
    assert project_tasks.risk_review_notifications.name == "project.risk_review_notifications"
    assert project_tasks.project_health_refresh.name == "project.project_health_refresh"
    assert project_tasks.retry_finance_posting.name == "project.retry_finance_posting"
