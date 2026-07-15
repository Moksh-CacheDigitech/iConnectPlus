"""ServiceAssignment lifecycle engine."""

from modules.service.domain.enums import (
    ServiceAssignmentStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceAssignmentState,
)


class ServiceAssignmentEngine:
    def activate(self, row) -> None:
        if row.status != ServiceAssignmentStatus.DRAFT.value:
            raise InvalidServiceAssignmentState("Only draft assignments can activate")
        row.status = ServiceAssignmentStatus.ACTIVE.value

    def complete(self, row) -> None:
        if row.status != ServiceAssignmentStatus.ACTIVE.value:
            raise InvalidServiceAssignmentState("Only active assignments can complete")
        row.status = ServiceAssignmentStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceAssignmentStatus.CANCELLED.value

