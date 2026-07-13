"""Delivery fulfillment engine."""

from decimal import Decimal

from modules.sales.domain.enums import DeliveryStatus, OrderStatus
from modules.sales.domain.exceptions import InvalidDocumentState, QuantityExceeded
from modules.sales.models.delivery import SalesDeliveryHeader
from modules.sales.models.order import SalesOrderHeader, SalesOrderLine
from modules.sales.service.engines.order_engine import OrderEngine


class DeliveryEngine:
    def __init__(self) -> None:
        self._order_engine = OrderEngine()

    def validate_order_for_delivery(self, order: SalesOrderHeader) -> None:
        if order.status not in {
            OrderStatus.CONFIRMED.value,
            OrderStatus.PROCESSING.value,
            OrderStatus.PARTIALLY_DELIVERED.value,
        }:
            raise InvalidDocumentState(
                "Order must be confirmed before creating a delivery"
            )

    def validate_delivery_qty(
        self, order_line: SalesOrderLine, quantity: Decimal
    ) -> None:
        remaining = self._order_engine.remaining_to_deliver(order_line)
        if quantity <= 0:
            raise QuantityExceeded("Delivery quantity must be greater than zero")
        if quantity > remaining:
            raise QuantityExceeded(
                f"Delivery quantity {quantity} exceeds remaining {remaining}"
            )

    def apply_to_order_line(
        self, order_line: SalesOrderLine, quantity: Decimal
    ) -> None:
        self.validate_delivery_qty(order_line, quantity)
        self._order_engine.apply_delivery_qty(order_line, quantity)

    def confirm_delivery(
        self,
        delivery: SalesDeliveryHeader,
        order: SalesOrderHeader,
        order_lines_by_id: dict,
    ) -> None:
        if delivery.status not in {
            DeliveryStatus.DRAFT.value,
            DeliveryStatus.PENDING.value,
        }:
            raise InvalidDocumentState("Delivery cannot be confirmed in its current state")

        active_lines = [
            line for line in delivery.lines if not getattr(line, "is_deleted", False)
        ]
        if not active_lines:
            raise InvalidDocumentState("Delivery must have at least one line")

        for line in active_lines:
            order_line = order_lines_by_id.get(line.order_line_id)
            if order_line is None:
                raise InvalidDocumentState(f"Order line {line.order_line_id} not found")
            qty = Decimal(str(line.quantity))
            self.apply_to_order_line(order_line, qty)
            line.status = "shipped"

        self._order_engine.refresh_header_amounts(order)
        delivery.status = DeliveryStatus.DELIVERED.value
        qty_total = sum(
            (Decimal(str(line.quantity)) for line in active_lines),
            start=Decimal("0"),
        )
        delivery.subtotal_amount = float(qty_total.quantize(Decimal("0.0001")))

    def remaining_qty_map(self, order: SalesOrderHeader) -> dict:
        return {
            line.id: self._order_engine.remaining_to_deliver(line)
            for line in order.lines
            if not getattr(line, "is_deleted", False)
        }
