"""Inventory task smoke tests."""

from modules.inventory.tasks import (
    batch_expiry_alerts,
    low_stock_alerts,
    recompute_available,
    reservation_cleanup,
    retry_finance_posting,
)


def test_task_names_registered():
    assert low_stock_alerts.name == "inventory.low_stock_alerts"
    assert batch_expiry_alerts.name == "inventory.batch_expiry_alerts"
    assert reservation_cleanup.name == "inventory.reservation_cleanup"
    assert recompute_available.name == "inventory.recompute_available"
    assert retry_finance_posting.name == "inventory.retry_finance_posting"
