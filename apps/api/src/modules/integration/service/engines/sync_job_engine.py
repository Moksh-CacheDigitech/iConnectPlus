"""SyncJob lifecycle engine."""

from modules.integration.domain.enums import (
    SyncJobStatus,
)
from modules.integration.domain.exceptions import (
    InvalidSyncJobState,
)


class SyncJobEngine:
    def submit(self, row) -> None:
        if row.status != SyncJobStatus.DRAFT.value:
            raise InvalidSyncJobState("Only draft sync jobs can be submitted")
        row.status = SyncJobStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != SyncJobStatus.SUBMITTED.value:
            raise InvalidSyncJobState("Only submitted sync jobs can be approved")
        row.status = SyncJobStatus.APPROVED.value

    def run(self, row) -> None:
        if row.status not in {SyncJobStatus.APPROVED.value, SyncJobStatus.QUEUED.value}:
            raise InvalidSyncJobState("Sync job must be approved or queued to run")
        row.status = SyncJobStatus.RUNNING.value

    def succeed(self, row) -> None:
        row.status = SyncJobStatus.SUCCEEDED.value

    def fail(self, row) -> None:
        row.status = SyncJobStatus.FAILED.value

    def cancel(self, row) -> None:
        row.status = SyncJobStatus.CANCELLED.value
