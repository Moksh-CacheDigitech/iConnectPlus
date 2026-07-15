"""Report lifecycle engine."""

from modules.integration.domain.enums import (
    ReportStatus,
)


class ReportEngine:
    def finalize(self, row) -> None:
        row.status = ReportStatus.FINALIZED.value
