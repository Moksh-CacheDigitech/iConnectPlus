"""ChangeRequest lifecycle engine."""

from modules.project.domain.enums import (
    ChangeRequestStatus,
)
from modules.project.domain.exceptions import (
    InvalidChangeRequestState,
)


class ChangeRequestEngine:
    def submit(self, row) -> None:
        if row.status != ChangeRequestStatus.DRAFT.value:
            raise InvalidChangeRequestState("Only draft change requests can be submitted")
        row.status = ChangeRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ChangeRequestStatus.SUBMITTED.value:
            raise InvalidChangeRequestState("Only submitted change requests can be approved")
        row.status = ChangeRequestStatus.APPROVED.value

    def reject(self, row) -> None:
        if row.status != ChangeRequestStatus.SUBMITTED.value:
            raise InvalidChangeRequestState("Only submitted change requests can be rejected")
        row.status = ChangeRequestStatus.REJECTED.value

    def implement(self, row) -> None:
        if row.status != ChangeRequestStatus.APPROVED.value:
            raise InvalidChangeRequestState("Only approved change requests can be implemented")
        row.status = ChangeRequestStatus.IMPLEMENTED.value

    def cancel(self, row) -> None:
        if row.status in {ChangeRequestStatus.IMPLEMENTED.value, ChangeRequestStatus.CANCELLED.value}:
            raise InvalidChangeRequestState("Change request already terminal")
        row.status = ChangeRequestStatus.CANCELLED.value

