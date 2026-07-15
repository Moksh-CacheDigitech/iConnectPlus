"""AssetDisposal lifecycle engine."""

from modules.asset.domain.enums import (
    AssetDisposalStatus,
)
from modules.asset.domain.exceptions import (
    InvalidAssetDisposalState,
)


class AssetDisposalEngine:
    def submit(self, row) -> None:
        if row.status != AssetDisposalStatus.DRAFT.value:
            raise InvalidAssetDisposalState("Only draft disposals can be submitted")
        row.status = AssetDisposalStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != AssetDisposalStatus.SUBMITTED.value:
            raise InvalidAssetDisposalState("Only submitted disposals can be approved")
        row.status = AssetDisposalStatus.APPROVED.value

    def post(self, row) -> None:
        if row.status != AssetDisposalStatus.APPROVED.value:
            raise InvalidAssetDisposalState("Only approved disposals can be posted")
        row.status = AssetDisposalStatus.POSTED.value

