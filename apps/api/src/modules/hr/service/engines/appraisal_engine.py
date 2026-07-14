"""Appraisal lifecycle engine."""

from modules.hr.domain.enums import AppraisalStatus
from modules.hr.domain.exceptions import InvalidAppraisalState


class AppraisalEngine:
    def finalize(self, row) -> None:
        if row.status != AppraisalStatus.DRAFT.value:
            raise InvalidAppraisalState("Only draft appraisals can be finalized")
        row.status = AppraisalStatus.FINAL.value
