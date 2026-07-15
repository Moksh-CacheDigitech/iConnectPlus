"""ServiceNotification lifecycle engine."""

from modules.service.domain.enums import (
    ServiceNotificationStatus,
)


class ServiceNotificationEngine:
    def archive(self, row) -> None:
        row.status = ServiceNotificationStatus.ARCHIVED.value

