"""ProjectTask lifecycle engine."""

from modules.project.domain.enums import (
    ProjectTaskStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectTaskState,
)


class ProjectTaskEngine:
    def start(self, row) -> None:
        if row.status not in {ProjectTaskStatus.OPEN.value, ProjectTaskStatus.APPROVED.value}:
            raise InvalidProjectTaskState("Task not startable")
        row.status = ProjectTaskStatus.IN_PROGRESS.value

    def block(self, row) -> None:
        if row.status != ProjectTaskStatus.IN_PROGRESS.value:
            raise InvalidProjectTaskState("Only in-progress tasks can be blocked")
        row.status = ProjectTaskStatus.BLOCKED.value

    def complete(self, row) -> None:
        if row.status not in {ProjectTaskStatus.IN_PROGRESS.value, ProjectTaskStatus.BLOCKED.value}:
            raise InvalidProjectTaskState("Task not completable")
        row.status = ProjectTaskStatus.COMPLETED.value

    def submit(self, row) -> None:
        if row.status not in {ProjectTaskStatus.OPEN.value, ProjectTaskStatus.IN_PROGRESS.value}:
            raise InvalidProjectTaskState("Task not submittable")
        row.status = ProjectTaskStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProjectTaskStatus.SUBMITTED.value:
            raise InvalidProjectTaskState("Only submitted tasks can be approved")
        row.status = ProjectTaskStatus.APPROVED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectTaskStatus.COMPLETED.value, ProjectTaskStatus.CANCELLED.value}:
            raise InvalidProjectTaskState("Task already terminal")
        row.status = ProjectTaskStatus.CANCELLED.value

