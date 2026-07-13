"""Sales return validation engine."""

from decimal import Decimal

from modules.sales.domain.enums import InvoiceStatus, ReturnStatus
from modules.sales.domain.exceptions import InvalidDocumentState, QuantityExceeded
from modules.sales.models.invoice import SalesInvoiceHeader, SalesInvoiceLine
from modules.sales.models.order import SalesOrderLine
from modules.sales.models.return_doc import SalesReturnHeader, SalesReturnLine


class ReturnEngine:
    def validate_invoice_for_return(self, invoice: SalesInvoiceHeader) -> None:
        if invoice.status not in {
            InvoiceStatus.POSTED.value,
            InvoiceStatus.PARTIALLY_PAID.value,
            InvoiceStatus.PAID.value,
        }:
            raise InvalidDocumentState("Returns require a posted invoice")

    def validate_returnable_qty(
        self,
        *,
        returned_qty: Decimal,
        invoiced_qty: Decimal,
        previously_returned: Decimal = Decimal("0"),
    ) -> None:
        if returned_qty <= 0:
            raise QuantityExceeded("Return quantity must be greater than zero")
        remaining = invoiced_qty - previously_returned
        if returned_qty > remaining:
            raise QuantityExceeded(
                f"Return quantity {returned_qty} exceeds remaining invoiced {remaining}"
            )

    def validate_against_invoice_line(
        self,
        return_line: SalesReturnLine,
        invoice_line: SalesInvoiceLine,
        *,
        previously_returned: Decimal = Decimal("0"),
    ) -> None:
        self.validate_returnable_qty(
            returned_qty=Decimal(str(return_line.quantity)),
            invoiced_qty=Decimal(str(invoice_line.quantity)),
            previously_returned=previously_returned,
        )

    def validate_against_order_line(
        self,
        return_line: SalesReturnLine,
        order_line: SalesOrderLine,
    ) -> None:
        self.validate_returnable_qty(
            returned_qty=Decimal(str(return_line.quantity)),
            invoiced_qty=Decimal(str(order_line.quantity_invoiced)),
            previously_returned=Decimal(str(order_line.quantity_returned)),
        )

    def apply_return_to_order_line(
        self, order_line: SalesOrderLine, quantity: Decimal
    ) -> None:
        self.validate_returnable_qty(
            returned_qty=quantity,
            invoiced_qty=Decimal(str(order_line.quantity_invoiced)),
            previously_returned=Decimal(str(order_line.quantity_returned)),
        )
        order_line.quantity_returned = float(
            (Decimal(str(order_line.quantity_returned)) + quantity).quantize(
                Decimal("0.0001")
            )
        )

    def validate_submittable(self, return_header: SalesReturnHeader) -> None:
        if return_header.status != ReturnStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft returns can be submitted")
        active = [
            line for line in return_header.lines if not getattr(line, "is_deleted", False)
        ]
        if not active:
            raise InvalidDocumentState("Return must have at least one line")

    def compute_line_total(self, line: SalesReturnLine) -> Decimal:
        net = Decimal(str(line.quantity)) * Decimal(str(line.unit_price))
        tax = Decimal(str(line.tax_amount))
        return (net + tax).quantize(Decimal("0.0001"))

    def apply_header_totals(self, return_header: SalesReturnHeader) -> None:
        active = [
            line for line in return_header.lines if not getattr(line, "is_deleted", False)
        ]
        subtotal = Decimal("0")
        tax = Decimal("0")
        for line in active:
            line_total = self.compute_line_total(line)
            line.line_total = float(line_total)
            subtotal += Decimal(str(line.quantity)) * Decimal(str(line.unit_price))
            tax += Decimal(str(line.tax_amount))
        return_header.subtotal_amount = float(subtotal.quantize(Decimal("0.0001")))
        return_header.tax_amount = float(tax.quantize(Decimal("0.0001")))
        return_header.total_amount = float((subtotal + tax).quantize(Decimal("0.0001")))
