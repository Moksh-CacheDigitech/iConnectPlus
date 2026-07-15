"""RetryQueue lifecycle engine."""

from modules.integration.domain.enums import (
    RetryQueueStatus,
)
from modules.integration.domain.exceptions import (
    InvalidRetryQueueState,
)


class RetryQueueEngine:
    def submit(self, row) -> None:
        if row.status not in {RetryQueueStatus.PENDING.value, RetryQueueStatus.EXHAUSTED.value}:
            raise InvalidRetryQueueState("Retry not reviewable")
        row.workflow_status = "submitted"

    def start(self, row) -> None:
        row.status = RetryQueueStatus.PROCESSING.value

    def succeed(self, row) -> None:
        row.status = RetryQueueStatus.SUCCEEDED.value

    def exhaust(self, row) -> None:
        row.status = RetryQueueStatus.EXHAUSTED.value

    def cancel(self, row) -> None:
        row.status = RetryQueueStatus.CANCELLED.value
