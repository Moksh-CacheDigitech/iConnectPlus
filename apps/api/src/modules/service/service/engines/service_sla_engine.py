"""ServiceSla lifecycle engine."""

from modules.service.domain.enums import (
    ServiceSlaStatus,
)


class ServiceSlaEngine:
    def activate(self, row) -> None:
        row.status = ServiceSlaStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ServiceSlaStatus.INACTIVE.value

