"""Purchase order lifecycle engine."""

from decimal import Decimal

from modules.procurement.domain.enums import OrderStatus
from modules.procurement.domain.exceptions import InvalidDocumentState
from modules.procurement.models.order import ProcOrderHeader, ProcOrderLine


class OrderEngine:
    CONFIRMABLE = {OrderStatus.DRAFT.value}
    RECEIVABLE = {
        OrderStatus.APPROVED.value,
        OrderStatus.SENT.value,
        OrderStatus.PARTIALLY_RECEIVED.value,
    }

    def validate_confirmable(self, order: ProcOrderHeader) -> None:
        if order.status not in self.CONFIRMABLE:
            raise InvalidDocumentState("Only draft orders can be confirmed")
        active_lines = [
            line for line in order.lines if not getattr(line, "is_deleted", False)
        ]
        if not active_lines:
            raise InvalidDocumentState("Order must have at least one line to confirm")

    def validate_receivable(self, order: ProcOrderHeader) -> None:
        if order.status not in self.RECEIVABLE:
            raise InvalidDocumentState("Order must be approved before receiving goods")

    def remaining_to_receive(self, line: ProcOrderLine) -> Decimal:
        ordered = Decimal(str(line.quantity))
        received = Decimal(str(line.quantity_received))
        remaining = ordered - received
        return remaining if remaining > 0 else Decimal("0")

    def remaining_to_invoice(self, line: ProcOrderLine) -> Decimal:
        ordered = Decimal(str(line.quantity))
        invoiced = Decimal(str(line.quantity_invoiced))
        remaining = ordered - invoiced
        return remaining if remaining > 0 else Decimal("0")

    def rollup_line_status(self, line: ProcOrderLine) -> str:
        ordered = Decimal(str(line.quantity))
        received = Decimal(str(line.quantity_received))
        if line.status == "cancelled":
            return "cancelled"
        if received <= 0:
            return "open"
        if received >= ordered:
            return "received"
        return "partially_received"

    def rollup_header_status(self, order: ProcOrderHeader) -> str:
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

        received_flags = []
        for line in active:
            ordered = Decimal(str(line.quantity))
            received = Decimal(str(line.quantity_received))
            if received <= 0:
                received_flags.append("none")
            elif received >= ordered:
                received_flags.append("full")
            else:
                received_flags.append("partial")

        if all(flag == "full" for flag in received_flags):
            return OrderStatus.RECEIVED.value
        if any(flag in {"partial", "full"} for flag in received_flags):
            return OrderStatus.PARTIALLY_RECEIVED.value
        if order.status == OrderStatus.SENT.value:
            return OrderStatus.SENT.value
        if order.status == OrderStatus.APPROVED.value:
            return OrderStatus.APPROVED.value
        return order.status

    def apply_receive_qty(self, line: ProcOrderLine, quantity: Decimal) -> None:
        line.quantity_received = float(
            (Decimal(str(line.quantity_received)) + quantity).quantize(Decimal("0.0001"))
        )
        line.status = self.rollup_line_status(line)

    def apply_invoice_qty(self, line: ProcOrderLine, quantity: Decimal) -> None:
        line.quantity_invoiced = float(
            (Decimal(str(line.quantity_invoiced)) + quantity).quantize(Decimal("0.0001"))
        )

    def refresh_header_amounts(self, order: ProcOrderHeader) -> None:
        active = [line for line in order.lines if not getattr(line, "is_deleted", False)]
        received_amount = Decimal("0")
        invoiced_amount = Decimal("0")
        for line in active:
            unit = Decimal(str(line.unit_cost))
            received_amount += Decimal(str(line.quantity_received)) * unit
            invoiced_amount += Decimal(str(line.quantity_invoiced)) * unit
        order.received_amount = float(received_amount.quantize(Decimal("0.0001")))
        order.invoiced_amount = float(invoiced_amount.quantize(Decimal("0.0001")))
        order.status = self.rollup_header_status(order)
