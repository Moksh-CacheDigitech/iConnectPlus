"""Inventory domain entities / results."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class StockMovementResult:
    balance_id: UUID
    ledger_id: UUID
    on_hand_qty: Decimal
    reserved_qty: Decimal
    available_qty: Decimal
    total_cost: Decimal | None = None
    already_processed: bool = False


@dataclass
class ReservationResult:
    reservation_id: UUID
    quantity_reserved: Decimal
    available_qty: Decimal
    status: str


@dataclass
class GrnReceiptResult:
    """Compatibility result for procurement InventoryReceiptPort."""

    grn_id: UUID
    order_id: UUID
    inventory_event_emitted: bool
    stock_updated: bool
