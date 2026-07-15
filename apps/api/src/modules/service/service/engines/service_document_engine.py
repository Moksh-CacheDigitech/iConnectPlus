"""ServiceDocument lifecycle engine."""

from modules.service.domain.enums import (
    ServiceDocumentStatus,
)


class ServiceDocumentEngine:
    def supersede(self, row) -> None:
        row.status = ServiceDocumentStatus.SUPERSEDED.value

    def archive(self, row) -> None:
        row.status = ServiceDocumentStatus.ARCHIVED.value

