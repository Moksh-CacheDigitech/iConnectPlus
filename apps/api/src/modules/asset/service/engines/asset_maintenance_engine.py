"""AssetMaintenance lifecycle engine."""

from modules.asset.domain.enums import (
    AssetMaintenanceStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetMaintenanceState,
)


class AssetMaintenanceEngine:
    def submit(self, row) -> None:
        if row.status != AssetMaintenanceStatus.DRAFT.value:
            raise InvalidAssetMaintenanceState("Only draft maintenance can be submitted")
        row.status = AssetMaintenanceStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetMaintenanceStatus.SUBMITTED.value:
            raise InvalidAssetMaintenanceState("Only submitted maintenance can be approved")
        row.status = AssetMaintenanceStatus.APPROVED.value

    def schedule(self, row) -> None:
        if row.status != AssetMaintenanceStatus.APPROVED.value:
            raise InvalidAssetMaintenanceState("Only approved maintenance can be scheduled")
        row.status = AssetMaintenanceStatus.SCHEDULED.value

    def start(self, row) -> None:
        if row.status not in {AssetMaintenanceStatus.APPROVED.value, AssetMaintenanceStatus.SCHEDULED.value}:
            raise InvalidAssetMaintenanceState("Maintenance not startable")
        row.status = AssetMaintenanceStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status not in {
            AssetMaintenanceStatus.APPROVED.value,
            AssetMaintenanceStatus.SCHEDULED.value,
            AssetMaintenanceStatus.IN_PROGRESS.value,
        }:
            raise InvalidAssetMaintenanceState("Maintenance not completable")
        row.status = AssetMaintenanceStatus.COMPLETED.value

