"""CartItem lifecycle engine."""

from modules.ecommerce.domain.enums import (
    CartItemStatus,
)


class CartItemEngine:
    def remove(self, row) -> None:
        row.status = CartItemStatus.REMOVED.value
