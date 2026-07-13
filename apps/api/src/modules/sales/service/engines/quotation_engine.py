"""Quotation lifecycle engine."""

from datetime import date
from decimal import Decimal

from modules.sales.domain.entities import DocumentTotals
from modules.sales.domain.enums import QuotationStatus
from modules.sales.domain.exceptions import InvalidConversion, InvalidDocumentState
from modules.sales.domain.value_objects import LineTotals
from modules.sales.models.quotation import SalesQuotationHeader, SalesQuotationLine


class QuotationEngine:
    def validate_convertible(self, quotation: SalesQuotationHeader) -> None:
        if quotation.status != QuotationStatus.ACCEPTED.value:
            raise InvalidConversion("Only accepted quotations can be converted to orders")
        if quotation.valid_until < date.today():
            raise InvalidConversion("Quotation has expired")

    def validate_editable(self, quotation: SalesQuotationHeader) -> None:
        if quotation.status not in {
            QuotationStatus.DRAFT.value,
            QuotationStatus.REJECTED.value,
        }:
            raise InvalidDocumentState("Quotation is not editable in its current state")

    def compute_line_totals(self, line: SalesQuotationLine) -> LineTotals:
        discount = Decimal(str(line.discount_amount))
        if discount == 0 and Decimal(str(line.discount_percent)) > 0:
            base = Decimal(str(line.quantity)) * Decimal(str(line.unit_price))
            discount = (
                base * Decimal(str(line.discount_percent)) / Decimal("100")
            ).quantize(Decimal("0.0001"))
        return LineTotals.compute(
            quantity=Decimal(str(line.quantity)),
            unit_price=Decimal(str(line.unit_price)),
            discount_amount=discount,
            tax_rate=Decimal(str(line.tax_rate)),
        )

    def apply_line_totals(self, line: SalesQuotationLine, totals: LineTotals) -> None:
        line.discount_amount = float(totals.discount_amount)
        line.tax_amount = float(totals.tax_amount)
        line.line_total = float(totals.line_total)

    def compute_header_totals(self, lines: list[SalesQuotationLine]) -> DocumentTotals:
        active = [line for line in lines if not getattr(line, "is_deleted", False)]
        subtotal = Decimal("0")
        discount = Decimal("0")
        tax = Decimal("0")
        for line in active:
            qty = Decimal(str(line.quantity))
            price = Decimal(str(line.unit_price))
            subtotal += qty * price
            discount += Decimal(str(line.discount_amount))
            tax += Decimal(str(line.tax_amount))
        total = (subtotal - discount + tax).quantize(Decimal("0.0001"))
        return DocumentTotals(
            subtotal_amount=subtotal.quantize(Decimal("0.0001")),
            discount_amount=discount.quantize(Decimal("0.0001")),
            tax_amount=tax.quantize(Decimal("0.0001")),
            total_amount=total,
        )

    def apply_header_totals(
        self, quotation: SalesQuotationHeader, totals: DocumentTotals
    ) -> None:
        quotation.subtotal_amount = float(totals.subtotal_amount)
        quotation.discount_amount = float(totals.discount_amount)
        quotation.tax_amount = float(totals.tax_amount)
        quotation.total_amount = float(totals.total_amount)
