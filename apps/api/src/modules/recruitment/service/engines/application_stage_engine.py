"""ApplicationStage lifecycle engine."""

from modules.recruitment.domain.enums import (
    ApplicationStageStatus,
)


class ApplicationStageEngine:
    def complete(self, row) -> None:
        row.status = ApplicationStageStatus.COMPLETED.value

    def skip(self, row) -> None:
        row.status = ApplicationStageStatus.SKIPPED.value

    def cancel(self, row) -> None:
        row.status = ApplicationStageStatus.CANCELLED.value

