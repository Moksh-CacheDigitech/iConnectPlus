"""Employment lifecycle engine."""

from modules.hr.domain.enums import EmploymentStatus
from modules.hr.domain.exceptions import InvalidEmploymentState


class EmploymentEngine:
    ACTIVE_SET = {"active", "probation", "confirmed"}

    def validate_activate(self, row) -> None:
        if row.status not in {"draft", "probation"}:
            raise InvalidEmploymentState("Employment must be draft/probation to activate")

    def apply_activate(self, row) -> None:
        self.validate_activate(row)
        row.status = EmploymentStatus.ACTIVE.value

    def apply_confirm(self, row) -> None:
        if row.status not in {"active", "probation"}:
            raise InvalidEmploymentState("Only active/probation employment can be confirmed")
        row.status = EmploymentStatus.CONFIRMED.value

    def apply_end(self, row) -> None:
        if row.status not in self.ACTIVE_SET:
            raise InvalidEmploymentState("Only active employment can be ended")
        row.status = EmploymentStatus.ENDED.value
