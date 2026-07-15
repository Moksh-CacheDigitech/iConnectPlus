"""AssetChecklist lifecycle engine."""

from modules.asset.domain.enums import (
    AssetChecklistStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetChecklistState,
)


class AssetChecklistEngine:
    def complete(self, row) -> None:
        if row.status != AssetChecklistStatus.DRAFT.value:
            raise InvalidAssetChecklistState("Only draft checklists can be completed")
        row.status = AssetChecklistStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = AssetChecklistStatus.CANCELLED.value

