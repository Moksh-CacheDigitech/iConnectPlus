"""EmployeeDocument lifecycle engine."""

from modules.hr.domain.enums import DocumentStatus, VerificationStatus
from modules.hr.domain.exceptions import InvalidEmployeeDocumentState


class EmployeeDocumentEngine:
    def verify(self, row) -> None:
        if row.verification_status == VerificationStatus.VERIFIED.value:
            raise InvalidEmployeeDocumentState("Document already verified")
        row.verification_status = VerificationStatus.VERIFIED.value

    def reject(self, row) -> None:
        row.verification_status = VerificationStatus.REJECTED.value

    def archive(self, row) -> None:
        row.status = DocumentStatus.ARCHIVED.value
