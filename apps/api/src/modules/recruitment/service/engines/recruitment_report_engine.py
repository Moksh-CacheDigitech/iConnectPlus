"""RecruitmentReport lifecycle engine."""

from modules.recruitment.domain.enums import (
    RecruitmentReportStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidRecruitmentReportState,
)


class RecruitmentReportEngine:
    def finalize(self, row) -> None:
        if row.status != RecruitmentReportStatus.DRAFT.value:
            raise InvalidRecruitmentReportState("Only draft reports can finalize")
        row.status = RecruitmentReportStatus.FINALIZED.value

