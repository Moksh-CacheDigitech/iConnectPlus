"""Unit tests for E-Commerce Celery task names."""

from modules.ecommerce import tasks


def test_ecommerce_task_names_registered():
    assert tasks.listing_publish_scheduler.name == "ecommerce.listing_publish_scheduler"
    assert tasks.inventory_sync_pull.name == "ecommerce.inventory_sync_pull"
    assert tasks.order_import_poller.name == "ecommerce.order_import_poller"
    assert tasks.sales_order_mapper.name == "ecommerce.sales_order_mapper"
    assert tasks.shipment_tracking_poller.name == "ecommerce.shipment_tracking_poller"
    assert tasks.cart_abandonment_notifier.name == "ecommerce.cart_abandonment_notifier"
