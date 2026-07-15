"""Promotion lifecycle engine."""

from modules.ecommerce.domain.enums import (
    PromotionStatus,
)


class PromotionEngine:
    def activate(self, row) -> None:
        row.status = PromotionStatus.ACTIVE.value

    def pause(self, row) -> None:
        row.status = PromotionStatus.PAUSED.value

    def expire(self, row) -> None:
        row.status = PromotionStatus.EXPIRED.value
