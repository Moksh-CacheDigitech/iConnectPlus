"""AssetReport lifecycle engine."""

from modules.asset.domain.enums import (
    AssetReportStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetReportState,
)


class AssetReportEngine:
    def finalize(self, row) -> None:
        if row.status != AssetReportStatus.DRAFT.value:
            raise InvalidAssetReportState("Only draft reports can be finalized")
        row.status = AssetReportStatus.FINALIZED.value

