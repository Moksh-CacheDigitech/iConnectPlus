"""Order lifecycle engine."""

from modules.ecommerce.domain.enums import (
    OrderStatus,
)
from modules.ecommerce.domain.exceptions import (
    InvalidOrderState,
)


class OrderEngine:
    def submit(self, row) -> None:
        if row.status != OrderStatus.NEW.value:
            raise InvalidOrderState("Only new orders can be submitted")
        row.status = OrderStatus.SUBMITTED.value

    def accept(self, row) -> None:
        if row.status not in {OrderStatus.SUBMITTED.value, OrderStatus.UNDER_REVIEW.value}:
            raise InvalidOrderState("Order not reviewable for acceptance")
        row.status = OrderStatus.ACCEPTED.value

    def cancel(self, row) -> None:
        row.status = OrderStatus.CANCELLED.value
