"""TaskDependency lifecycle engine."""

from modules.project.domain.enums import (
    TaskDependencyStatus,
)


class TaskDependencyEngine:
    def activate(self, row) -> None:
        row.status = TaskDependencyStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = TaskDependencyStatus.INACTIVE.value

