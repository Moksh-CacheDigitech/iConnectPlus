"""Onboarding lifecycle engine."""

from modules.recruitment.domain.enums import (
    OnboardingStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidOnboardingState,
)


class OnboardingEngine:
    def submit(self, row) -> None:
        if row.status != OnboardingStatus.DRAFT.value:
            raise InvalidOnboardingState("Only draft onboarding can be submitted")
        row.status = OnboardingStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != OnboardingStatus.SUBMITTED.value:
            raise InvalidOnboardingState("Only submitted onboarding can be approved")
        row.status = OnboardingStatus.IN_PROGRESS.value

    def start(self, row) -> None:
        row.status = OnboardingStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != OnboardingStatus.IN_PROGRESS.value:
            raise InvalidOnboardingState("Only in-progress onboarding can complete")
        if row.employee_id is None:
            raise InvalidOnboardingState("Employee must exist before completion")
        row.status = OnboardingStatus.COMPLETED.value

    def fail(self, row) -> None:
        row.status = OnboardingStatus.FAILED.value

    def cancel(self, row) -> None:
        row.status = OnboardingStatus.CANCELLED.value

