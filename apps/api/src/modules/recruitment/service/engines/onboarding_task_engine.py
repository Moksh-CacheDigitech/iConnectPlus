"""OnboardingTask lifecycle engine."""

from modules.recruitment.domain.enums import (
    OnboardingTaskStatus,
)


class OnboardingTaskEngine:
    def start(self, row) -> None:
        row.status = OnboardingTaskStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        row.status = OnboardingTaskStatus.COMPLETED.value

    def waive(self, row) -> None:
        row.status = OnboardingTaskStatus.WAIVED.value

    def block(self, row) -> None:
        row.status = OnboardingTaskStatus.BLOCKED.value

    def cancel(self, row) -> None:
        row.status = OnboardingTaskStatus.CANCELLED.value

