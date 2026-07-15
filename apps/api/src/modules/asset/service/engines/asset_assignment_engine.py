"""AssetAssignment lifecycle engine."""

from modules.asset.domain.enums import (
    AssetAssignmentStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetAssignmentState,
)


class AssetAssignmentEngine:
    def submit(self, row) -> None:
        if row.status != AssetAssignmentStatus.DRAFT.value:
            raise InvalidAssetAssignmentState("Only draft assignments can be submitted")
        row.status = AssetAssignmentStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetAssignmentStatus.SUBMITTED.value:
            raise InvalidAssetAssignmentState("Only submitted assignments can be approved")
        row.status = AssetAssignmentStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != AssetAssignmentStatus.APPROVED.value:
            raise InvalidAssetAssignmentState("Only approved assignments can be activated")
        row.status = AssetAssignmentStatus.ACTIVE.value

    def return_assignment(self, row) -> None:
        if row.status != AssetAssignmentStatus.ACTIVE.value:
            raise InvalidAssetAssignmentState("Only active assignments can be returned")
        row.status = AssetAssignmentStatus.RETURNED.value

