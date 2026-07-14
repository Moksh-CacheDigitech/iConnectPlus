"""InterviewFeedback lifecycle engine."""

from modules.recruitment.domain.enums import (
    InterviewFeedbackStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidInterviewFeedbackState,
)


class InterviewFeedbackEngine:
    def submit(self, row) -> None:
        if row.status != InterviewFeedbackStatus.DRAFT.value:
            raise InvalidInterviewFeedbackState("Only draft feedback can be submitted")
        row.status = InterviewFeedbackStatus.SUBMITTED.value

    def lock(self, row) -> None:
        if row.status != InterviewFeedbackStatus.SUBMITTED.value:
            raise InvalidInterviewFeedbackState("Only submitted feedback can be locked")
        row.status = InterviewFeedbackStatus.LOCKED.value

