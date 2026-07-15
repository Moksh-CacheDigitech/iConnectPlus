"""AssetAudit lifecycle engine."""

from modules.asset.domain.enums import (
    AssetAuditStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetAuditState,
)


class AssetAuditEngine:
    def start(self, row) -> None:
        if row.status != AssetAuditStatus.PLANNED.value:
            raise InvalidAssetAuditState("Only planned audits can be started")
        row.status = AssetAuditStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status not in {
            AssetAuditStatus.PLANNED.value,
            AssetAuditStatus.IN_PROGRESS.value,
        }:
            raise InvalidAssetAuditState("Audit not completable")
        row.status = AssetAuditStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == AssetAuditStatus.COMPLETED.value:
            raise InvalidAssetAuditState("Completed audits cannot be cancelled")
        row.status = AssetAuditStatus.CANCELLED.value

