"""Payment lifecycle engine."""

from modules.ecommerce.domain.enums import (
    PaymentStatus,
)


class PaymentEngine:
    def authorize(self, row) -> None:
        row.status = PaymentStatus.AUTHORIZED.value

    def capture(self, row) -> None:
        row.status = PaymentStatus.CAPTURED.value

    def fail(self, row) -> None:
        row.status = PaymentStatus.FAILED.value

    def refund(self, row) -> None:
        row.status = PaymentStatus.REFUNDED.value
