"""Notification lifecycle engine."""

from modules.integration.domain.enums import (
    NotificationStatus,
)


class NotificationEngine:
    def archive(self, row) -> None:
        row.status = NotificationStatus.ARCHIVED.value

    def acknowledge(self, row) -> None:
        row.delivery_status = "read"
