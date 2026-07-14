"""ProjectDocument lifecycle engine."""

from modules.project.domain.enums import (
    ProjectDocumentStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectState,
)


class ProjectDocumentEngine:
    def supersede(self, row) -> None:
        if row.status != ProjectDocumentStatus.ACTIVE.value:
            raise InvalidProjectState("Only active documents can be superseded")
        row.status = ProjectDocumentStatus.SUPERSEDED.value

    def archive(self, row) -> None:
        if row.status not in {ProjectDocumentStatus.ACTIVE.value, ProjectDocumentStatus.SUPERSEDED.value}:
            raise InvalidProjectState("Document not archivable")
        row.status = ProjectDocumentStatus.ARCHIVED.value

