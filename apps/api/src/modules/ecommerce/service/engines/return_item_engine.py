"""ReturnItem lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ReturnItemStatus,
)


class ReturnItemEngine:
    def approve(self, row) -> None:
        row.status = ReturnItemStatus.APPROVED.value

    def receive(self, row) -> None:
        row.status = ReturnItemStatus.RECEIVED.value

    def refund(self, row) -> None:
        row.status = ReturnItemStatus.REFUNDED.value
