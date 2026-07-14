"""Training lifecycle engine."""

from modules.hr.domain.enums import TrainingStatus
from modules.hr.domain.exceptions import InvalidTrainingState


class TrainingEngine:
    def start(self, row) -> None:
        if row.status != TrainingStatus.PLANNED.value:
            raise InvalidTrainingState("Only planned training can start")
        row.status = TrainingStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status not in {TrainingStatus.PLANNED.value, TrainingStatus.IN_PROGRESS.value}:
            raise InvalidTrainingState("Training cannot be completed from current status")
        row.status = TrainingStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == TrainingStatus.COMPLETED.value:
            raise InvalidTrainingState("Completed training cannot be cancelled")
        row.status = TrainingStatus.CANCELLED.value
