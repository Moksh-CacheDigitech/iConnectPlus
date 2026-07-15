"""MessageQueue lifecycle engine."""

from modules.integration.domain.enums import (
    MessageQueueStatus,
)


class MessageQueueEngine:
    def pause(self, row) -> None:
        row.status = MessageQueueStatus.PAUSED.value

    def activate(self, row) -> None:
        row.status = MessageQueueStatus.ACTIVE.value

    def drain(self, row) -> None:
        row.status = MessageQueueStatus.DRAINED.value
