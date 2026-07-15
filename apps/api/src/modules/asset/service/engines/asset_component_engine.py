"""AssetComponent lifecycle engine."""

from modules.asset.domain.enums import (
    AssetComponentStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetComponentState,
)


class AssetComponentEngine:
    def replace(self, row) -> None:
        if row.status != AssetComponentStatus.ACTIVE.value:
            raise InvalidAssetComponentState("Only active components can be replaced")
        row.status = AssetComponentStatus.REPLACED.value

    def dispose(self, row) -> None:
        row.status = AssetComponentStatus.DISPOSED.value

