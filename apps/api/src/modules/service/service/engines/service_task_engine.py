"""ServiceTask lifecycle engine."""

from modules.service.domain.enums import (
    ServiceTaskStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceTaskState,
)


class ServiceTaskEngine:
    def start(self, row) -> None:
        if row.status != ServiceTaskStatus.PENDING.value:
            raise InvalidServiceTaskState("Only pending tasks can start")
        row.status = ServiceTaskStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != ServiceTaskStatus.IN_PROGRESS.value:
            raise InvalidServiceTaskState("Only in-progress tasks can complete")
        row.status = ServiceTaskStatus.COMPLETED.value

    def block(self, row) -> None:
        row.status = ServiceTaskStatus.BLOCKED.value

    def cancel(self, row) -> None:
        row.status = ServiceTaskStatus.CANCELLED.value

