"""PaymentTransaction lifecycle engine."""

from modules.ecommerce.domain.enums import (
    PaymentTransactionStatus,
)


class PaymentTransactionEngine:
    def post(self, row) -> None:
        row.status = PaymentTransactionStatus.POSTED.value

    def fail(self, row) -> None:
        row.status = PaymentTransactionStatus.FAILED.value
