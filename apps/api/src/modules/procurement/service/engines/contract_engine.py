"""Vendor contract lifecycle engine."""

from datetime import date

from modules.procurement.domain.enums import ContractStatus
from modules.procurement.domain.exceptions import ContractExpired, InvalidDocumentState
from modules.procurement.models.contract import ProcVendorContract


class ContractEngine:
    def validate_editable(self, contract: ProcVendorContract) -> None:
        if contract.status not in {ContractStatus.DRAFT.value}:
            raise InvalidDocumentState("Contract is not editable in its current state")

    def validate_active(self, contract: ProcVendorContract, *, as_of: date | None = None) -> None:
        check_date = as_of or date.today()
        if contract.status != ContractStatus.ACTIVE.value:
            raise InvalidDocumentState("Contract is not active")
        if contract.end_date < check_date:
            raise ContractExpired()

    def validate_activatable(self, contract: ProcVendorContract) -> None:
        if contract.status != ContractStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft contracts can be activated")
        if contract.end_date < contract.start_date:
            raise InvalidDocumentState("Contract end date must be on or after start date")
        active_lines = [
            line for line in contract.lines if not getattr(line, "is_deleted", False)
        ]
        if not active_lines:
            raise InvalidDocumentState("Contract must have at least one line")

    def refresh_status_by_date(self, contract: ProcVendorContract) -> None:
        if contract.status == ContractStatus.TERMINATED.value:
            return
        today = date.today()
        if contract.status == ContractStatus.ACTIVE.value and contract.end_date < today:
            contract.status = ContractStatus.EXPIRED.value
