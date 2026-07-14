"""Resume lifecycle engine."""

from modules.recruitment.domain.enums import (
    ResumeStatus,
)


class ResumeEngine:
    def supersede(self, row) -> None:
        row.status = ResumeStatus.SUPERSEDED.value
        row.is_primary = False

    def archive(self, row) -> None:
        row.status = ResumeStatus.ARCHIVED.value

