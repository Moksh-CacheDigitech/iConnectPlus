"""Application lifecycle engine."""

from modules.recruitment.domain.enums import (
    ApplicationStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidApplicationState,
)


class ApplicationEngine:
    def advance(self, row, *, stage: str) -> None:
        allowed = {
            ApplicationStatus.APPLIED.value: ApplicationStatus.SCREENING.value,
            ApplicationStatus.SCREENING.value: ApplicationStatus.INTERVIEW.value,
            ApplicationStatus.INTERVIEW.value: ApplicationStatus.SELECTED.value,
            ApplicationStatus.SELECTED.value: ApplicationStatus.OFFER.value,
            ApplicationStatus.OFFER.value: ApplicationStatus.HIRED.value,
        }
        if row.status not in allowed or allowed[row.status] != stage:
            raise InvalidApplicationState("Invalid application stage transition")
        row.status = stage
        row.current_stage_code = stage

    def reject(self, row, *, reason: str | None = None) -> None:
        row.status = ApplicationStatus.REJECTED.value
        row.rejection_reason = reason

    def hold(self, row) -> None:
        row.status = ApplicationStatus.ON_HOLD.value

    def withdraw(self, row) -> None:
        row.status = ApplicationStatus.WITHDRAWN.value

