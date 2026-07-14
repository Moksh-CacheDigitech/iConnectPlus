"""ProjectComment lifecycle engine."""

from modules.project.domain.enums import (
    ProjectCommentStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectState,
)


class ProjectCommentEngine:
    def edit(self, row) -> None:
        if row.status not in {ProjectCommentStatus.ACTIVE.value, ProjectCommentStatus.EDITED.value}:
            raise InvalidProjectState("Comment not editable")
        row.status = ProjectCommentStatus.EDITED.value

    def soft_delete(self, row) -> None:
        row.status = ProjectCommentStatus.DELETED_SOFT.value

