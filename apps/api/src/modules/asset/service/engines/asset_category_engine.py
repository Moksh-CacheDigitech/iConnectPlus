"""AssetCategory lifecycle engine."""

from modules.asset.domain.enums import (
    AssetCategoryStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetCategoryState,
)


class AssetCategoryEngine:
    def activate(self, row) -> None:
        row.status = AssetCategoryStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        if row.status != AssetCategoryStatus.ACTIVE.value:
            raise InvalidAssetCategoryState("Only active categories can be deactivated")
        row.status = AssetCategoryStatus.INACTIVE.value

