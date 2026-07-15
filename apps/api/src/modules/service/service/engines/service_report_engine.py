"""ServiceReport lifecycle engine."""

from modules.service.domain.enums import (
    ServiceReportStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceReportState,
)


class ServiceReportEngine:
    def finalize(self, row) -> None:
        if row.status != ServiceReportStatus.DRAFT.value:
            raise InvalidServiceReportState("Only draft reports can finalize")
        row.status = ServiceReportStatus.FINALIZED.value

