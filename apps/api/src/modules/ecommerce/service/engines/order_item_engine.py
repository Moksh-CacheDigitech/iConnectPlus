"""OrderItem lifecycle engine."""

from modules.ecommerce.domain.enums import (
    OrderItemStatus,
)


class OrderItemEngine:
    def allocate(self, row) -> None:
        row.status = OrderItemStatus.ALLOCATED.value

    def ship(self, row) -> None:
        row.status = OrderItemStatus.SHIPPED.value

    def cancel(self, row) -> None:
        row.status = OrderItemStatus.CANCELLED.value
