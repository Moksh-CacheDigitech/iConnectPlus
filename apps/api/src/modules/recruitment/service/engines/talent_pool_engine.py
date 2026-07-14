"""TalentPool lifecycle engine."""

from modules.recruitment.domain.enums import (
    TalentPoolStatus,
)


class TalentPoolEngine:
    def remove(self, row) -> None:
        row.status = TalentPoolStatus.REMOVED.value

    def mark_hired_out(self, row) -> None:
        row.status = TalentPoolStatus.HIRED_OUT.value

