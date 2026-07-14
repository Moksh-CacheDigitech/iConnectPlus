"""ProjectIssue lifecycle engine."""

from modules.project.domain.enums import (
    ProjectIssueStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectIssueState,
)


class ProjectIssueEngine:
    def start(self, row) -> None:
        if row.status != ProjectIssueStatus.OPEN.value:
            raise InvalidProjectIssueState("Only open issues can start")
        row.status = ProjectIssueStatus.IN_PROGRESS.value

    def resolve(self, row) -> None:
        if row.status != ProjectIssueStatus.IN_PROGRESS.value:
            raise InvalidProjectIssueState("Only in-progress issues can resolve")
        row.status = ProjectIssueStatus.RESOLVED.value

    def close(self, row) -> None:
        if row.status != ProjectIssueStatus.RESOLVED.value:
            raise InvalidProjectIssueState("Only resolved issues can close")
        row.status = ProjectIssueStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectIssueStatus.CLOSED.value, ProjectIssueStatus.CANCELLED.value}:
            raise InvalidProjectIssueState("Issue already terminal")
        row.status = ProjectIssueStatus.CANCELLED.value

