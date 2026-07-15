"""AssetDepreciation lifecycle engine."""

from modules.asset.domain.enums import (
    AssetDepreciationStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetDepreciationState,
)


class AssetDepreciationEngine:
    def calculate(self, row) -> None:
        if row.status != AssetDepreciationStatus.DRAFT.value:
            raise InvalidAssetDepreciationState("Only draft depreciation can be calculated")
        row.status = AssetDepreciationStatus.CALCULATED.value

    def post(self, row) -> None:
        if row.status != AssetDepreciationStatus.CALCULATED.value:
            raise InvalidAssetDepreciationState("Only calculated depreciation can be posted")
        row.status = AssetDepreciationStatus.POSTED.value

    def fail(self, row) -> None:
        row.status = AssetDepreciationStatus.FAILED.value

    def reverse(self, row) -> None:
        if row.status != AssetDepreciationStatus.POSTED.value:
            raise InvalidAssetDepreciationState("Only posted depreciation can be reversed")
        row.status = AssetDepreciationStatus.REVERSED.value

