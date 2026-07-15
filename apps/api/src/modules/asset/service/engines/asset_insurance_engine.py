"""AssetInsurance lifecycle engine."""

from modules.asset.domain.enums import (
    AssetInsuranceStatus,
)


class AssetInsuranceEngine:
    def expire(self, row) -> None:
        row.status = AssetInsuranceStatus.EXPIRED.value

    def cancel(self, row) -> None:
        row.status = AssetInsuranceStatus.CANCELLED.value

