"""ListingInventory lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ListingInventoryStatus,
)


class ListingInventoryEngine:
    def activate(self, row) -> None:
        row.status = ListingInventoryStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ListingInventoryStatus.INACTIVE.value
