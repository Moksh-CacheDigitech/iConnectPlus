"""Purchase invoice calculation engine."""

from decimal import Decimal

from modules.procurement.domain.entities import DocumentTotals
from modules.procurement.domain.enums import InvoiceStatus
from modules.procurement.domain.exceptions import InvalidDocumentState
from modules.procurement.domain.value_objects import LineTotals
from modules.procurement.models.invoice import ProcInvoiceHeader, ProcInvoiceLine


class InvoiceEngine:
    def validate_editable(self, invoice: ProcInvoiceHeader) -> None:
        if invoice.status != InvoiceStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft invoices can be edited")

    def validate_postable(self, invoice: ProcInvoiceHeader) -> None:
        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.SUBMITTED.value,
        }:
            raise InvalidDocumentState("Invoice cannot be posted in its current state")
        active = [line for line in invoice.lines if not getattr(line, "is_deleted", False)]
        if not active:
            raise InvalidDocumentState("Invoice must have at least one line")

    def compute_line_totals(self, line: ProcInvoiceLine) -> LineTotals:
        return LineTotals.compute(
            quantity=Decimal(str(line.quantity)),
            unit_cost=Decimal(str(line.unit_cost)),
            tax_rate=Decimal(str(line.tax_rate)),
        )

    def apply_line_totals(self, line: ProcInvoiceLine, totals: LineTotals) -> None:
        line.tax_amount = float(totals.tax_amount)
        line.line_total = float(totals.line_total)

    def compute_header_totals(self, lines: list[ProcInvoiceLine]) -> DocumentTotals:
        active = [line for line in lines if not getattr(line, "is_deleted", False)]
        subtotal = Decimal("0")
        discount = Decimal("0")
        tax = Decimal("0")
        for line in active:
            subtotal += Decimal(str(line.quantity)) * Decimal(str(line.unit_cost))
            tax += Decimal(str(line.tax_amount))
        total = (subtotal - discount + tax).quantize(Decimal("0.0001"))
        return DocumentTotals(
            subtotal_amount=subtotal.quantize(Decimal("0.0001")),
            discount_amount=discount.quantize(Decimal("0.0001")),
            tax_amount=tax.quantize(Decimal("0.0001")),
            total_amount=total,
        )

    def apply_header_totals(
        self, invoice: ProcInvoiceHeader, totals: DocumentTotals
    ) -> None:
        invoice.subtotal_amount = float(totals.subtotal_amount)
        invoice.discount_amount = float(totals.discount_amount)
        invoice.tax_amount = float(totals.tax_amount)
        invoice.total_amount = float(totals.total_amount)
        self.refresh_balance_due(invoice)

    def refresh_balance_due(self, invoice: ProcInvoiceHeader) -> None:
        total = Decimal(str(invoice.total_amount))
        paid = Decimal(str(invoice.amount_paid))
        balance = (total - paid).quantize(Decimal("0.0001"))
        if balance < 0:
            balance = Decimal("0")
        invoice.balance_due = float(balance)

        if invoice.status in {
            InvoiceStatus.POSTED.value,
            InvoiceStatus.PARTIALLY_PAID.value,
            InvoiceStatus.PAID.value,
        }:
            if balance == 0 and paid > 0:
                invoice.status = InvoiceStatus.PAID.value
            elif paid > 0 and balance > 0:
                invoice.status = InvoiceStatus.PARTIALLY_PAID.value
