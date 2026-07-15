"""SalesChannel lifecycle engine."""

from modules.ecommerce.domain.enums import (
    SalesChannelStatus,
)


class SalesChannelEngine:
    def activate(self, row) -> None:
        row.status = SalesChannelStatus.ACTIVE.value
        row.is_active = True

    def pause(self, row) -> None:
        row.status = SalesChannelStatus.PAUSED.value
        row.is_active = False

    def retire(self, row) -> None:
        row.status = SalesChannelStatus.RETIRED.value
        row.is_active = False
