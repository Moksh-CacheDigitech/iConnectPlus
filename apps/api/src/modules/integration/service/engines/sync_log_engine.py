"""SyncLog lifecycle engine."""

from modules.integration.domain.enums import (
    SyncLogStatus,
)


class SyncLogEngine:
    def record(self, row) -> None:
        row.status = SyncLogStatus.RECORDED.value
