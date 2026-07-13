"""Purchase requisition lifecycle engine."""

from decimal import Decimal

from modules.procurement.domain.entities import DocumentTotals
from modules.procurement.domain.enums import RequisitionStatus
from modules.procurement.domain.exceptions import InvalidDocumentState
from modules.procurement.domain.value_objects import LineTotals
from modules.procurement.models.requisition import ProcRequisitionHeader, ProcRequisitionLine


class RequisitionEngine:
    def validate_editable(self, requisition: ProcRequisitionHeader) -> None:
        if requisition.status not in {
            RequisitionStatus.DRAFT.value,
            RequisitionStatus.REJECTED.value,
        }:
            raise InvalidDocumentState("Requisition is not editable in its current state")

    def validate_submittable(self, requisition: ProcRequisitionHeader) -> None:
        if requisition.status != RequisitionStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft requisitions can be submitted")
        active = [
            line for line in requisition.lines if not getattr(line, "is_deleted", False)
        ]
        if not active:
            raise InvalidDocumentState("Requisition must have at least one line")

    def validate_convertible(self, requisition: ProcRequisitionHeader) -> None:
        if requisition.status != RequisitionStatus.APPROVED.value:
            raise InvalidDocumentState("Only approved requisitions can be converted to RFQ")

    def compute_line_totals(self, line: ProcRequisitionLine) -> LineTotals:
        unit_cost = Decimal(str(line.estimated_unit_cost or 0))
        return LineTotals.compute(
            quantity=Decimal(str(line.quantity)),
            unit_cost=unit_cost,
            tax_rate=Decimal("0"),
        )

    def apply_line_totals(self, line: ProcRequisitionLine, totals: LineTotals) -> None:
        line.tax_amount = float(totals.tax_amount)
        line.line_total = float(totals.line_total)

    def compute_header_totals(self, lines: list[ProcRequisitionLine]) -> DocumentTotals:
        active = [line for line in lines if not getattr(line, "is_deleted", False)]
        subtotal = Decimal("0")
        tax = Decimal("0")
        for line in active:
            unit = Decimal(str(line.estimated_unit_cost or 0))
            subtotal += Decimal(str(line.quantity)) * unit
            tax += Decimal(str(line.tax_amount))
        total = (subtotal + tax).quantize(Decimal("0.0001"))
        return DocumentTotals(
            subtotal_amount=subtotal.quantize(Decimal("0.0001")),
            discount_amount=Decimal("0"),
            tax_amount=tax.quantize(Decimal("0.0001")),
            total_amount=total,
        )

    def apply_header_totals(
        self, requisition: ProcRequisitionHeader, totals: DocumentTotals
    ) -> None:
        requisition.subtotal_amount = float(totals.subtotal_amount)
        requisition.tax_amount = float(totals.tax_amount)
        requisition.total_amount = float(totals.total_amount)
