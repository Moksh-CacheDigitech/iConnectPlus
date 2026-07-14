"""BackgroundVerification lifecycle engine."""

from modules.recruitment.domain.enums import (
    BackgroundVerificationStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidBackgroundVerificationState,
)


class BackgroundVerificationEngine:
    def submit(self, row) -> None:
        if row.status != BackgroundVerificationStatus.DRAFT.value:
            raise InvalidBackgroundVerificationState("Only draft BGV can be submitted")
        row.status = BackgroundVerificationStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status not in {
            BackgroundVerificationStatus.SUBMITTED.value,
            BackgroundVerificationStatus.IN_PROGRESS.value,
        }:
            raise InvalidBackgroundVerificationState("BGV not approvable")
        row.status = BackgroundVerificationStatus.CLEARED.value
        row.result = "clear"

    def start_progress(self, row) -> None:
        row.status = BackgroundVerificationStatus.IN_PROGRESS.value

    def fail(self, row) -> None:
        row.status = BackgroundVerificationStatus.FAILED.value
        row.result = "adverse"

    def waive(self, row) -> None:
        row.status = BackgroundVerificationStatus.WAIVED.value

    def cancel(self, row) -> None:
        row.status = BackgroundVerificationStatus.CANCELLED.value

