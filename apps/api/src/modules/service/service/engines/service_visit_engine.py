"""ServiceVisit lifecycle engine."""

from modules.service.domain.enums import (
    ServiceVisitStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceVisitState,
)


class ServiceVisitEngine:
    def check_in(self, row) -> None:
        if row.status != ServiceVisitStatus.PLANNED.value:
            raise InvalidServiceVisitState("Only planned visits can check in")
        row.status = ServiceVisitStatus.CHECKED_IN.value

    def complete(self, row) -> None:
        if row.status != ServiceVisitStatus.CHECKED_IN.value:
            raise InvalidServiceVisitState("Only checked-in visits can complete")
        row.status = ServiceVisitStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceVisitStatus.CANCELLED.value

