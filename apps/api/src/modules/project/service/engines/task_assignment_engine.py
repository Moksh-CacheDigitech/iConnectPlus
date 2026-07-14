"""TaskAssignment lifecycle engine."""

from modules.project.domain.enums import (
    TaskAssignmentStatus,
)
from modules.project.domain.exceptions import (
    InvalidTaskAssignmentState,
)


class TaskAssignmentEngine:
    def complete(self, row) -> None:
        if row.status != TaskAssignmentStatus.ACTIVE.value:
            raise InvalidTaskAssignmentState("Only active assignments can complete")
        row.status = TaskAssignmentStatus.COMPLETED.value

    def remove(self, row) -> None:
        if row.status == TaskAssignmentStatus.REMOVED.value:
            raise InvalidTaskAssignmentState("Assignment already removed")
        row.status = TaskAssignmentStatus.REMOVED.value

