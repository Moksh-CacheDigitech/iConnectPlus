"""Interview lifecycle engine."""

from modules.recruitment.domain.enums import (
    InterviewStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidInterviewState,
)


class InterviewEngine:
    def schedule(self, row) -> None:
        row.status = InterviewStatus.SCHEDULED.value
        row.result = "pending"

    def complete(self, row) -> None:
        if row.status != InterviewStatus.SCHEDULED.value:
            raise InvalidInterviewState("Only scheduled interviews can complete")
        row.status = InterviewStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = InterviewStatus.CANCELLED.value

    def mark_no_show(self, row) -> None:
        row.status = InterviewStatus.NO_SHOW.value

