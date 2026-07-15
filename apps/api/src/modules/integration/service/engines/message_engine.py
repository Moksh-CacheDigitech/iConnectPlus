"""Message lifecycle engine."""

from modules.integration.domain.enums import (
    MessageStatus,
)


class MessageEngine:
    def start_processing(self, row) -> None:
        row.status = MessageStatus.PROCESSING.value

    def succeed(self, row) -> None:
        row.status = MessageStatus.SUCCEEDED.value

    def fail(self, row) -> None:
        row.status = MessageStatus.FAILED.value

    def dead_letter(self, row) -> None:
        row.status = MessageStatus.DEAD_LETTERED.value

    def cancel(self, row) -> None:
        row.status = MessageStatus.CANCELLED.value
