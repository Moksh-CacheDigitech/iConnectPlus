"""ShippingTracking lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ShippingTrackingStatus,
)


class ShippingTrackingEngine:
    def record(self, row) -> None:
        row.status = ShippingTrackingStatus.RECORDED.value
