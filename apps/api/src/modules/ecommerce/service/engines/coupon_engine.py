"""Coupon lifecycle engine."""

from modules.ecommerce.domain.enums import (
    CouponStatus,
)


class CouponEngine:
    def activate(self, row) -> None:
        row.status = CouponStatus.ACTIVE.value

    def exhaust(self, row) -> None:
        row.status = CouponStatus.EXHAUSTED.value

    def expire(self, row) -> None:
        row.status = CouponStatus.EXPIRED.value
