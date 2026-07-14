"""RecruitmentSource lifecycle engine."""

from modules.recruitment.domain.enums import (
    ActiveInactive,
)


class RecruitmentSourceEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
        row.is_active = False

