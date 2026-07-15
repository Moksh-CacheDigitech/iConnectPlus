"""AssetWarranty lifecycle engine."""

from modules.asset.domain.enums import (
    AssetWarrantyStatus,
)


class AssetWarrantyEngine:
    def expire(self, row) -> None:
        row.status = AssetWarrantyStatus.EXPIRED.value

    def void(self, row) -> None:
        row.status = AssetWarrantyStatus.VOID.value

