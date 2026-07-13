"""No-op inventory adapter until Inventory module (Sprint 7)."""

from uuid import UUID

from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.domain.entities import GrnReceiptResult
from modules.procurement.service.inventory.port import InventoryReceiptPort


class NoOpInventoryAdapter:
    """Stub adapter that satisfies InventoryReceiptPort without stock updates."""

    def receive_goods(
        self,
        ctx: TenantContext,
        *,
        grn_id: UUID,
        order_id: UUID,
        warehouse_reference: UUID,
    ) -> GrnReceiptResult:
        return GrnReceiptResult(
            grn_id=grn_id,
            order_id=order_id,
            inventory_event_emitted=False,
            stock_updated=False,
        )


def inventory_adapter() -> InventoryReceiptPort:
    return NoOpInventoryAdapter()
