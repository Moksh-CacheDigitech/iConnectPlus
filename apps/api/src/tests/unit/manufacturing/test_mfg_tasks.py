"""Manufacturing Celery task registration smoke tests."""

from modules.manufacturing import tasks


def test_task_names_registered():
    assert tasks.machine_breakdown_alerts.name == "manufacturing.machine_breakdown_alerts"
    assert tasks.capacity_overload_alerts.name == "manufacturing.capacity_overload_alerts"
    assert tasks.wip_reconcile.name == "manufacturing.wip_reconcile"
    assert tasks.retry_finance_posting.name == "manufacturing.retry_finance_posting"
    assert tasks.scrap_threshold_alerts.name == "manufacturing.scrap_threshold_alerts"
