"""Inventory receipt port for GRN confirmation."""

from typing import Protocol
from uuid import UUID

from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.domain.entities import GrnReceiptResult


class InventoryReceiptPort(Protocol):
    def receive_goods(
        self,
        ctx: TenantContext,
        *,
        grn_id: UUID,
        order_id: UUID,
        warehouse_reference: UUID,
    ) -> GrnReceiptResult: ...
