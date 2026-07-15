"""ReturnRequest lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ReturnRequestStatus,
)
from modules.ecommerce.domain.exceptions import (
    InvalidReturnRequestState,
)


class ReturnRequestEngine:
    def submit(self, row) -> None:
        if row.status != ReturnRequestStatus.REQUESTED.value:
            raise InvalidReturnRequestState("Only requested returns can be submitted")
        row.status = ReturnRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ReturnRequestStatus.SUBMITTED.value:
            raise InvalidReturnRequestState("Only submitted returns can be approved")
        row.status = ReturnRequestStatus.APPROVED.value

    def reject(self, row) -> None:
        row.status = ReturnRequestStatus.REJECTED.value

    def close(self, row) -> None:
        row.status = ReturnRequestStatus.CLOSED.value
