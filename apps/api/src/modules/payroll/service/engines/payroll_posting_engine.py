"""PayrollPosting lifecycle engine."""

from modules.payroll.domain.enums import (
    PostingStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidPayrollPostingState,
)


class PayrollPostingEngine:
    def submit(self, row) -> None:
        if row.status != PostingStatus.DRAFT.value:
            raise InvalidPayrollPostingState("Only draft posting can be submitted")
        row.status = PostingStatus.SUBMITTED.value

    def mark_posted(self, row) -> None:
        if row.status != PostingStatus.SUBMITTED.value:
            raise InvalidPayrollPostingState("Only submitted posting can post")
        row.status = PostingStatus.POSTED.value

    def mark_failed(self, row, message: str) -> None:
        row.status = PostingStatus.FAILED.value
        row.error_message = message

