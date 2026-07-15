"""ServiceCategory lifecycle engine."""

from modules.service.domain.enums import (
    ServiceCategoryStatus,
)


class ServiceCategoryEngine:
    def activate(self, row) -> None:
        row.status = ServiceCategoryStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ServiceCategoryStatus.INACTIVE.value

