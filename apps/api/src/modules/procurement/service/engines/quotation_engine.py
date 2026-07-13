"""Vendor quotation lifecycle engine."""

from datetime import date
from decimal import Decimal

from modules.procurement.domain.entities import DocumentTotals
from modules.procurement.domain.enums import VendorQuotationStatus
from modules.procurement.domain.exceptions import (
    InvalidConversion,
    InvalidDocumentState,
    VendorQuotationExpired,
)
from modules.procurement.domain.value_objects import LineTotals
from modules.procurement.models.vendor_quotation import (
    ProcVendorQuotationHeader,
    ProcVendorQuotationLine,
)


class QuotationEngine:
    def validate_convertible(self, quotation: ProcVendorQuotationHeader) -> None:
        if quotation.status != VendorQuotationStatus.SELECTED.value:
            raise InvalidConversion("Only selected vendor quotations can be converted to PO")
        if quotation.valid_until < date.today():
            raise VendorQuotationExpired()

    def validate_editable(self, quotation: ProcVendorQuotationHeader) -> None:
        if quotation.status not in {
            VendorQuotationStatus.DRAFT.value,
            VendorQuotationStatus.REJECTED.value,
        }:
            raise InvalidDocumentState("Vendor quotation is not editable in its current state")

    def validate_submittable(self, quotation: ProcVendorQuotationHeader) -> None:
        if quotation.status != VendorQuotationStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft quotations can be submitted")
        active = [
            line for line in quotation.lines if not getattr(line, "is_deleted", False)
        ]
        if not active:
            raise InvalidDocumentState("Vendor quotation must have at least one line")

    def compute_line_totals(self, line: ProcVendorQuotationLine) -> LineTotals:
        return LineTotals.compute(
            quantity=Decimal(str(line.quantity)),
            unit_cost=Decimal(str(line.unit_cost)),
            tax_rate=Decimal(str(line.tax_rate)),
        )

    def apply_line_totals(self, line: ProcVendorQuotationLine, totals: LineTotals) -> None:
        line.tax_amount = float(totals.tax_amount)
        line.line_total = float(totals.line_total)

    def compute_header_totals(self, lines: list[ProcVendorQuotationLine]) -> DocumentTotals:
        active = [line for line in lines if not getattr(line, "is_deleted", False)]
        subtotal = Decimal("0")
        tax = Decimal("0")
        for line in active:
            subtotal += Decimal(str(line.quantity)) * Decimal(str(line.unit_cost))
            tax += Decimal(str(line.tax_amount))
        total = (subtotal + tax).quantize(Decimal("0.0001"))
        return DocumentTotals(
            subtotal_amount=subtotal.quantize(Decimal("0.0001")),
            discount_amount=Decimal("0"),
            tax_amount=tax.quantize(Decimal("0.0001")),
            total_amount=total,
        )

    def apply_header_totals(
        self, quotation: ProcVendorQuotationHeader, totals: DocumentTotals
    ) -> None:
        quotation.subtotal_amount = float(totals.subtotal_amount)
        quotation.tax_amount = float(totals.tax_amount)
        quotation.total_amount = float(totals.total_amount)
