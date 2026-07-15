"""AssetTransfer lifecycle engine."""

from modules.asset.domain.enums import (
    AssetTransferStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetTransferState,
)


class AssetTransferEngine:
    def complete(self, row) -> None:
        if row.status != AssetTransferStatus.DRAFT.value:
            raise InvalidAssetTransferState("Only draft transfers can be completed")
        row.status = AssetTransferStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == AssetTransferStatus.COMPLETED.value:
            raise InvalidAssetTransferState("Completed transfers cannot be cancelled")
        row.status = AssetTransferStatus.CANCELLED.value

