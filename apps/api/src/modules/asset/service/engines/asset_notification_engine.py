"""AssetNotification lifecycle engine."""

from modules.asset.domain.enums import (
    AssetNotificationStatus,
)


class AssetNotificationEngine:
    def archive(self, row) -> None:
        row.status = AssetNotificationStatus.ARCHIVED.value

