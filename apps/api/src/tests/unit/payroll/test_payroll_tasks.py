"""Unit tests for payroll Celery tasks."""

from modules.payroll import tasks as payroll_tasks


def test_payroll_task_names_registered():
    assert payroll_tasks.payroll_run_scheduler.name == "payroll.payroll_run_scheduler"
    assert payroll_tasks.payslip_generation.name == "payroll.payslip_generation"
    assert payroll_tasks.loan_installment_processor.name == "payroll.loan_installment_processor"
    assert payroll_tasks.bonus_reminders.name == "payroll.bonus_reminders"
    assert payroll_tasks.payroll_post_retry.name == "payroll.payroll_post_retry"
    assert payroll_tasks.refresh_payroll_summary.name == "payroll.refresh_payroll_summary"
