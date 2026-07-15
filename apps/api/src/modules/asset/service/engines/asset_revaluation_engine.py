"""AssetRevaluation lifecycle engine."""

from modules.asset.domain.enums import (
    AssetRevaluationStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetRevaluationState,
)


class AssetRevaluationEngine:
    def submit(self, row) -> None:
        if row.status != AssetRevaluationStatus.DRAFT.value:
            raise InvalidAssetRevaluationState("Only draft revaluations can be submitted")
        row.status = AssetRevaluationStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetRevaluationStatus.SUBMITTED.value:
            raise InvalidAssetRevaluationState("Only submitted revaluations can be approved")
        row.status = AssetRevaluationStatus.APPROVED.value

    def post(self, row) -> None:
        if row.status != AssetRevaluationStatus.APPROVED.value:
            raise InvalidAssetRevaluationState("Only approved revaluations can be posted")
        row.status = AssetRevaluationStatus.POSTED.value

