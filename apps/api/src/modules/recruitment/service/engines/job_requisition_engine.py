"""JobRequisition lifecycle engine."""

from modules.recruitment.domain.enums import (
    JobRequisitionStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidJobRequisitionState,
)


class JobRequisitionEngine:
    def submit(self, row) -> None:
        if row.status != JobRequisitionStatus.DRAFT.value:
            raise InvalidJobRequisitionState("Only draft requisitions can be submitted")
        row.status = JobRequisitionStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != JobRequisitionStatus.SUBMITTED.value:
            raise InvalidJobRequisitionState("Only submitted requisitions can be approved")
        row.status = JobRequisitionStatus.APPROVED.value

    def open(self, row) -> None:
        if row.status not in {JobRequisitionStatus.APPROVED.value, JobRequisitionStatus.ON_HOLD.value}:
            raise InvalidJobRequisitionState("Requisition not openable")
        row.status = JobRequisitionStatus.OPEN.value

    def fill(self, row) -> None:
        if row.status != JobRequisitionStatus.OPEN.value:
            raise InvalidJobRequisitionState("Only open requisitions can be filled")
        row.status = JobRequisitionStatus.FILLED.value

    def close(self, row) -> None:
        if row.status not in {JobRequisitionStatus.OPEN.value, JobRequisitionStatus.FILLED.value}:
            raise InvalidJobRequisitionState("Requisition not closable")
        row.status = JobRequisitionStatus.CLOSED.value

    def hold(self, row) -> None:
        if row.status not in {JobRequisitionStatus.OPEN.value, JobRequisitionStatus.APPROVED.value}:
            raise InvalidJobRequisitionState("Requisition not holdable")
        row.status = JobRequisitionStatus.ON_HOLD.value

    def cancel(self, row) -> None:
        if row.status in {JobRequisitionStatus.CLOSED.value, JobRequisitionStatus.CANCELLED.value}:
            raise InvalidJobRequisitionState("Requisition already terminal")
        row.status = JobRequisitionStatus.CANCELLED.value

    def reject(self, row) -> None:
        if row.status != JobRequisitionStatus.SUBMITTED.value:
            raise InvalidJobRequisitionState("Only submitted requisitions can be rejected")
        row.status = JobRequisitionStatus.REJECTED.value

