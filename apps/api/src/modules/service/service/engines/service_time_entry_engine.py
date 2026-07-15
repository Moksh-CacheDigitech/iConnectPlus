"""ServiceTimeEntry lifecycle engine."""

from modules.service.domain.enums import (
    ServiceTimeEntryStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceTimeEntryState,
)


class ServiceTimeEntryEngine:
    def submit(self, row) -> None:
        if row.status != ServiceTimeEntryStatus.DRAFT.value:
            raise InvalidServiceTimeEntryState("Only draft time entries can be submitted")
        row.status = ServiceTimeEntryStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceTimeEntryStatus.SUBMITTED.value:
            raise InvalidServiceTimeEntryState("Only submitted time entries can be approved")
        row.status = ServiceTimeEntryStatus.APPROVED.value

    def void(self, row) -> None:
        row.status = ServiceTimeEntryStatus.VOID.value

