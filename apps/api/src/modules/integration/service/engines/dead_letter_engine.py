"""DeadLetter lifecycle engine."""

from modules.integration.domain.enums import (
    DeadLetterStatus,
)
from modules.integration.domain.exceptions import (
    InvalidDeadLetterState,
)


class DeadLetterEngine:
    def reprocess(self, row) -> None:
        if row.status != DeadLetterStatus.OPEN.value:
            raise InvalidDeadLetterState("Only open dead letters can be reprocessed")
        row.status = DeadLetterStatus.REPROCESSED.value

    def discard(self, row) -> None:
        row.status = DeadLetterStatus.DISCARDED.value
