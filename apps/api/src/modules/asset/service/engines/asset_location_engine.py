"""AssetLocation lifecycle engine."""

from modules.asset.domain.enums import (
    AssetLocationStatus,
)


class AssetLocationEngine:
    def mark_historical(self, row) -> None:
        row.status = AssetLocationStatus.HISTORICAL.value
        row.is_current = False

