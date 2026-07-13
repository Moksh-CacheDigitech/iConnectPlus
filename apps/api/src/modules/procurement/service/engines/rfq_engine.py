"""RFQ lifecycle engine."""

from datetime import date
from decimal import Decimal

from modules.procurement.domain.enums import RequisitionStatus, RfqStatus
from modules.procurement.domain.exceptions import InvalidConversion, InvalidDocumentState
from modules.procurement.models.requisition import ProcRequisitionHeader
from modules.procurement.models.rfq import ProcRfqHeader


class RfqEngine:
    def validate_editable(self, rfq: ProcRfqHeader) -> None:
        if rfq.status not in {RfqStatus.DRAFT.value}:
            raise InvalidDocumentState("RFQ is not editable in its current state")

    def validate_publishable(self, rfq: ProcRfqHeader) -> None:
        if rfq.status != RfqStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft RFQs can be published")
        active_lines = [line for line in rfq.lines if not getattr(line, "is_deleted", False)]
        if not active_lines:
            raise InvalidDocumentState("RFQ must have at least one line")
        if not rfq.vendors:
            raise InvalidDocumentState("RFQ must have at least one invited vendor")
        if rfq.closing_date < date.today():
            raise InvalidDocumentState("RFQ closing date must be in the future")

    def validate_from_requisition(self, requisition: ProcRequisitionHeader) -> None:
        if requisition.status != RequisitionStatus.APPROVED.value:
            raise InvalidConversion("Only approved requisitions can be converted to RFQ")

    def remaining_qty_map(self, rfq: ProcRfqHeader) -> dict:
        return {
            line.id: Decimal(str(line.quantity))
            for line in rfq.lines
            if not getattr(line, "is_deleted", False)
        }
