"""CustomerCart lifecycle engine."""

from modules.ecommerce.domain.enums import (
    CustomerCartStatus,
)


class CustomerCartEngine:
    def convert(self, row) -> None:
        row.status = CustomerCartStatus.CONVERTED.value

    def abandon(self, row) -> None:
        row.status = CustomerCartStatus.ABANDONED.value

    def cancel(self, row) -> None:
        row.status = CustomerCartStatus.CANCELLED.value
