"""Sales order lifecycle engine."""

from decimal import Decimal

from modules.sales.domain.enums import OrderStatus
from modules.sales.domain.exceptions import InvalidDocumentState
from modules.sales.models.order import SalesOrderHeader, SalesOrderLine


class OrderEngine:
    CONFIRMABLE = {OrderStatus.DRAFT.value}

    def validate_confirmable(self, order: SalesOrderHeader) -> None:
        if order.status not in self.CONFIRMABLE:
            raise InvalidDocumentState("Only draft orders can be confirmed")
        active_lines = [
            line for line in order.lines if not getattr(line, "is_deleted", False)
        ]
        if not active_lines:
            raise InvalidDocumentState("Order must have at least one line to confirm")

    def remaining_to_deliver(self, line: SalesOrderLine) -> Decimal:
        ordered = Decimal(str(line.quantity))
        delivered = Decimal(str(line.quantity_delivered))
        remaining = ordered - delivered
        return remaining if remaining > 0 else Decimal("0")

    def remaining_to_invoice(self, line: SalesOrderLine) -> Decimal:
        ordered = Decimal(str(line.quantity))
        invoiced = Decimal(str(line.quantity_invoiced))
        remaining = ordered - invoiced
        return remaining if remaining > 0 else Decimal("0")

    def rollup_line_status(self, line: SalesOrderLine) -> str:
        ordered = Decimal(str(line.quantity))
        delivered = Decimal(str(line.quantity_delivered))
        if line.status == "cancelled":
            return "cancelled"
        if delivered <= 0:
            return "open"
        if delivered >= ordered:
            return "delivered"
        return "partially_delivered"

    def rollup_header_status(self, order: SalesOrderHeader) -> str:
        if order.status == OrderStatus.CANCELLED.value:
            return OrderStatus.CANCELLED.value
        if order.status == OrderStatus.CLOSED.value:
            return OrderStatus.CLOSED.value

        active = [
            line
            for line in order.lines
            if not getattr(line, "is_deleted", False) and line.status != "cancelled"
        ]
        if not active:
            return order.status

        delivered_flags = []
        for line in active:
            ordered = Decimal(str(line.quantity))
            delivered = Decimal(str(line.quantity_delivered))
            if delivered <= 0:
                delivered_flags.append("none")
            elif delivered >= ordered:
                delivered_flags.append("full")
            else:
                delivered_flags.append("partial")

        if all(flag == "full" for flag in delivered_flags):
            return OrderStatus.DELIVERED.value
        if any(flag in {"partial", "full"} for flag in delivered_flags):
            return OrderStatus.PARTIALLY_DELIVERED.value
        if order.status == OrderStatus.CONFIRMED.value:
            return OrderStatus.CONFIRMED.value
        return order.status

    def apply_delivery_qty(self, line: SalesOrderLine, quantity: Decimal) -> None:
        line.quantity_delivered = float(
            (Decimal(str(line.quantity_delivered)) + quantity).quantize(Decimal("0.0001"))
        )
        line.status = self.rollup_line_status(line)

    def apply_invoice_qty(self, line: SalesOrderLine, quantity: Decimal) -> None:
        line.quantity_invoiced = float(
            (Decimal(str(line.quantity_invoiced)) + quantity).quantize(Decimal("0.0001"))
        )

    def refresh_header_amounts(self, order: SalesOrderHeader) -> None:
        active = [line for line in order.lines if not getattr(line, "is_deleted", False)]
        delivered_amount = Decimal("0")
        invoiced_amount = Decimal("0")
        for line in active:
            unit = Decimal(str(line.unit_price))
            delivered_amount += Decimal(str(line.quantity_delivered)) * unit
            invoiced_amount += Decimal(str(line.quantity_invoiced)) * unit
        order.delivered_amount = float(delivered_amount.quantize(Decimal("0.0001")))
        order.invoiced_amount = float(invoiced_amount.quantize(Decimal("0.0001")))
        order.status = self.rollup_header_status(order)
