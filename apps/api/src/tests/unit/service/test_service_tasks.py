"""Unit tests for service Celery tasks."""

from modules.service import tasks as service_tasks


def test_service_task_names_registered():
    assert service_tasks.sla_breach_monitor.name == "service.sla_breach_monitor"
    assert service_tasks.work_order_reminders.name == "service.work_order_reminders"
    assert service_tasks.preventive_service_scheduler.name == "service.preventive_service_scheduler"
    assert service_tasks.service_contract_expiry.name == "service.service_contract_expiry"
    assert service_tasks.customer_feedback_reminders.name == "service.customer_feedback_reminders"
    assert service_tasks.retry_finance_posting.name == "service.retry_finance_posting"
