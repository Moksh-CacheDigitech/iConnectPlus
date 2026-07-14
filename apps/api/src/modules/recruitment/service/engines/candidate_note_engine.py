"""CandidateNote lifecycle engine."""

from modules.recruitment.domain.enums import (
    CandidateNoteStatus,
)


class CandidateNoteEngine:
    def archive(self, row) -> None:
        row.status = CandidateNoteStatus.ARCHIVED.value

