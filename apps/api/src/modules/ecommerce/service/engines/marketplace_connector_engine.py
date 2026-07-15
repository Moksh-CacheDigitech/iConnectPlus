"""MarketplaceConnector lifecycle engine."""

from modules.ecommerce.domain.enums import (
    MarketplaceConnectorStatus,
)
from modules.ecommerce.domain.exceptions import (
    InvalidMarketplaceConnectorState,
)


class MarketplaceConnectorEngine:
    def submit(self, row) -> None:
        if row.status != MarketplaceConnectorStatus.DRAFT.value:
            raise InvalidMarketplaceConnectorState("Only draft connectors can be submitted")
        row.status = MarketplaceConnectorStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != MarketplaceConnectorStatus.SUBMITTED.value:
            raise InvalidMarketplaceConnectorState("Only submitted connectors can be approved")
        row.status = MarketplaceConnectorStatus.APPROVED.value

    def sync(self, row) -> None:
        row.status = MarketplaceConnectorStatus.ACTIVE.value

    def pause(self, row) -> None:
        row.status = MarketplaceConnectorStatus.PAUSED.value

    def mark_failed(self, row) -> None:
        row.status = MarketplaceConnectorStatus.FAILED.value
