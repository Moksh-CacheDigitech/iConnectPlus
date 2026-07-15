"""Unit tests for asset Celery tasks."""

from modules.asset import tasks as asset_tasks


def test_asset_task_names_registered():
    assert asset_tasks.maintenance_due_alerts.name == "asset.maintenance_due_alerts"
    assert asset_tasks.warranty_expiry_alerts.name == "asset.warranty_expiry_alerts"
    assert asset_tasks.insurance_expiry_alerts.name == "asset.insurance_expiry_alerts"
    assert asset_tasks.depreciation_scheduler.name == "asset.depreciation_scheduler"
    assert asset_tasks.asset_audit_reminders.name == "asset.asset_audit_reminders"
    assert asset_tasks.retry_finance_posting.name == "asset.retry_finance_posting"
