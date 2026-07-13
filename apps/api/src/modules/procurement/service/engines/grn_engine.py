"""GRN fulfillment engine."""

from decimal import Decimal

from modules.procurement.domain.enums import GrnStatus, OrderStatus
from modules.procurement.domain.exceptions import InvalidDocumentState, QuantityExceeded
from modules.procurement.models.grn import ProcGrnHeader
from modules.procurement.models.order import ProcOrderHeader, ProcOrderLine
from modules.procurement.service.engines.order_engine import OrderEngine


class GrnEngine:
    def __init__(self) -> None:
        self._order_engine = OrderEngine()

    def validate_order_for_grn(self, order: ProcOrderHeader) -> None:
        self._order_engine.validate_receivable(order)

    def validate_receive_qty(self, order_line: ProcOrderLine, quantity: Decimal) -> None:
        remaining = self._order_engine.remaining_to_receive(order_line)
        if quantity <= 0:
            raise QuantityExceeded("Receipt quantity must be greater than zero")
        if quantity > remaining:
            raise QuantityExceeded(
                f"Receipt quantity {quantity} exceeds remaining {remaining}"
            )

    def apply_to_order_line(self, order_line: ProcOrderLine, quantity: Decimal) -> None:
        self.validate_receive_qty(order_line, quantity)
        self._order_engine.apply_receive_qty(order_line, quantity)

    def confirm_grn(
        self,
        grn: ProcGrnHeader,
        order: ProcOrderHeader,
        order_lines_by_id: dict,
    ) -> None:
        if grn.status not in {GrnStatus.DRAFT.value, GrnStatus.PENDING.value}:
            raise InvalidDocumentState("GRN cannot be confirmed in its current state")
        if order.status == OrderStatus.CANCELLED.value:
            raise InvalidDocumentState("Cannot receive against a cancelled order")

        active_lines = [
            line for line in grn.lines if not getattr(line, "is_deleted", False)
        ]
        if not active_lines:
            raise InvalidDocumentState("GRN must have at least one line")

        for line in active_lines:
            order_line = order_lines_by_id.get(line.order_line_id)
            if order_line is None:
                raise InvalidDocumentState(f"Order line {line.order_line_id} not found")
            qty = Decimal(str(line.quantity)) - Decimal(str(line.quantity_rejected))
            if qty > 0:
                self.apply_to_order_line(order_line, qty)
            line.status = "received"

        self._order_engine.refresh_header_amounts(order)
        grn.status = GrnStatus.RECEIVED.value
        qty_total = sum(
            (Decimal(str(line.quantity)) for line in active_lines),
            start=Decimal("0"),
        )
        grn.subtotal_amount = float(qty_total.quantize(Decimal("0.0001")))

    def remaining_qty_map(self, order: ProcOrderHeader) -> dict:
        return {
            line.id: self._order_engine.remaining_to_receive(line)
            for line in order.lines
            if not getattr(line, "is_deleted", False)
        }
