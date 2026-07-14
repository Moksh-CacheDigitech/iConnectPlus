"""ProjectReport lifecycle engine."""

from modules.project.domain.enums import (
    ProjectReportStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectReportState,
)


class ProjectReportEngine:
    def finalize(self, row) -> None:
        if row.status != ProjectReportStatus.DRAFT.value:
            raise InvalidProjectReportState("Only draft reports can finalize")
        row.status = ProjectReportStatus.FINALIZED.value

