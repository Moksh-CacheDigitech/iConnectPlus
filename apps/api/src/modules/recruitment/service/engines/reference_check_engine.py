"""ReferenceCheck lifecycle engine."""

from modules.recruitment.domain.enums import (
    ReferenceCheckStatus,
)


class ReferenceCheckEngine:
    def contact(self, row) -> None:
        row.status = ReferenceCheckStatus.CONTACTED.value

    def complete(self, row) -> None:
        row.status = ReferenceCheckStatus.COMPLETED.value

    def decline(self, row) -> None:
        row.status = ReferenceCheckStatus.DECLINED.value

    def cancel(self, row) -> None:
        row.status = ReferenceCheckStatus.CANCELLED.value

