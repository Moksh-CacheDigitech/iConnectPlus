"""ListingPrice lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ListingPriceStatus,
)


class ListingPriceEngine:
    def activate(self, row) -> None:
        row.status = ListingPriceStatus.ACTIVE.value

    def expire(self, row) -> None:
        row.status = ListingPriceStatus.EXPIRED.value

    def supersede(self, row) -> None:
        row.status = ListingPriceStatus.SUPERSEDED.value
