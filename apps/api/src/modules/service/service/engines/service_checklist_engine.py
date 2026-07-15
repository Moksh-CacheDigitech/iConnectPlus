"""ServiceChecklist lifecycle engine."""

from modules.service.domain.enums import (
    ServiceChecklistStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceChecklistState,
)


class ServiceChecklistEngine:
    def complete(self, row) -> None:
        if row.status != ServiceChecklistStatus.DRAFT.value:
            raise InvalidServiceChecklistState("Only draft checklists can complete")
        row.status = ServiceChecklistStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceChecklistStatus.CANCELLED.value

