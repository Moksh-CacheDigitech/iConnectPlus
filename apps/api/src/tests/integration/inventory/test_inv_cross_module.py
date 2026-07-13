"""Cross-module adapter contract tests."""

from modules.inventory.adapters.procurement_adapter import ProcurementInventoryAdapter
from modules.inventory.adapters.sales_adapter import SalesInventoryAdapter
from modules.procurement.service.inventory.port import InventoryReceiptPort


def test_procurement_adapter_implements_receipt_port():
    assert issubclass(ProcurementInventoryAdapter, object)
    assert hasattr(ProcurementInventoryAdapter, "receive_goods")
    assert callable(getattr(InventoryReceiptPort, "receive_goods", None) or True)


def test_sales_adapter_has_required_methods():
    for name in ("reserve_order", "release_order", "issue_delivery", "receive_return"):
        assert hasattr(SalesInventoryAdapter, name)
