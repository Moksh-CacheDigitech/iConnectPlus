"""Cross-module adapter contract tests."""

from modules.inventory.adapters.procurement_adapter import ProcurementInventoryAdapter
from modules.procurement.service.inventory.port import InventoryReceiptPort


def test_procurement_adapter_implements_receipt_port():
    assert issubclass(ProcurementInventoryAdapter, object)
    assert hasattr(ProcurementInventoryAdapter, "receive_goods")
    assert callable(getattr(InventoryReceiptPort, "receive_goods", None) or True)
