"""CandidateDocument lifecycle engine."""

from modules.recruitment.domain.enums import (
    CandidateDocumentStatus,
)


class CandidateDocumentEngine:
    def verify(self, row) -> None:
        row.status = CandidateDocumentStatus.VERIFIED.value
        row.verified_flag = True

    def reject(self, row) -> None:
        row.status = CandidateDocumentStatus.REJECTED.value

    def archive(self, row) -> None:
        row.status = CandidateDocumentStatus.ARCHIVED.value

