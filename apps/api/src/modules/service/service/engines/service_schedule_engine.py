"""ServiceSchedule lifecycle engine."""

from modules.service.domain.enums import (
    ServiceScheduleStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceScheduleState,
)


class ServiceScheduleEngine:
    def confirm(self, row) -> None:
        if row.status != ServiceScheduleStatus.PLANNED.value:
            raise InvalidServiceScheduleState("Only planned schedules can confirm")
        row.status = ServiceScheduleStatus.CONFIRMED.value

    def start(self, row) -> None:
        if row.status not in {ServiceScheduleStatus.PLANNED.value, ServiceScheduleStatus.CONFIRMED.value}:
            raise InvalidServiceScheduleState("Schedule not startable")
        row.status = ServiceScheduleStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != ServiceScheduleStatus.IN_PROGRESS.value:
            raise InvalidServiceScheduleState("Only in-progress schedules can complete")
        row.status = ServiceScheduleStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceScheduleStatus.CANCELLED.value

