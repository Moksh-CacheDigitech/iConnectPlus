"""EventSubscription lifecycle engine."""

from modules.integration.domain.enums import (
    EventSubscriptionStatus,
)


class EventSubscriptionEngine:
    def pause(self, row) -> None:
        row.status = EventSubscriptionStatus.PAUSED.value

    def activate(self, row) -> None:
        row.status = EventSubscriptionStatus.ACTIVE.value

    def cancel(self, row) -> None:
        row.status = EventSubscriptionStatus.CANCELLED.value
