"""ProjectNotification lifecycle engine."""

from modules.project.domain.enums import (
    ProjectNotificationStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectState,
)


class ProjectNotificationEngine:
    def archive(self, row) -> None:
        if row.status != ProjectNotificationStatus.ACTIVE.value:
            raise InvalidProjectState("Only active notifications can archive")
        row.status = ProjectNotificationStatus.ARCHIVED.value

