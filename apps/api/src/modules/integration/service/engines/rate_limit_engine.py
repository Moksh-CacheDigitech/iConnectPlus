"""RateLimit lifecycle engine."""

from modules.integration.domain.enums import (
    RateLimitStatus,
)


class RateLimitEngine:
    def activate(self, row) -> None:
        row.status = RateLimitStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = RateLimitStatus.INACTIVE.value
