"""ServiceResolution lifecycle engine."""

from modules.service.domain.enums import (
    ServiceResolutionStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceResolutionState,
)


class ServiceResolutionEngine:
    def submit(self, row) -> None:
        if row.status != ServiceResolutionStatus.DRAFT.value:
            raise InvalidServiceResolutionState("Only draft resolutions can be submitted")
        row.status = ServiceResolutionStatus.SUBMITTED.value

    def complete(self, row) -> None:
        if row.status != ServiceResolutionStatus.SUBMITTED.value:
            raise InvalidServiceResolutionState("Only submitted resolutions can complete")
        row.status = ServiceResolutionStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceResolutionStatus.CANCELLED.value

