"""ProductListing lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ProductListingStatus,
)
from modules.ecommerce.domain.exceptions import (
    InvalidProductListingState,
)


class ProductListingEngine:
    def submit(self, row) -> None:
        if row.status != ProductListingStatus.DRAFT.value:
            raise InvalidProductListingState("Only draft listings can be submitted")
        row.status = ProductListingStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProductListingStatus.SUBMITTED.value:
            raise InvalidProductListingState("Only submitted listings can be approved")
        row.status = ProductListingStatus.APPROVED.value

    def publish(self, row) -> None:
        if row.status not in {ProductListingStatus.APPROVED.value, ProductListingStatus.UNPUBLISHED.value}:
            raise InvalidProductListingState("Only approved listings can be published")
        row.status = ProductListingStatus.PUBLISHED.value

    def unpublish(self, row) -> None:
        row.status = ProductListingStatus.UNPUBLISHED.value

    def archive(self, row) -> None:
        row.status = ProductListingStatus.ARCHIVED.value
