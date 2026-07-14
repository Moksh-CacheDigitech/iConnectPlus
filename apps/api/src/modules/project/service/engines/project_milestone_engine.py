"""ProjectMilestone lifecycle engine."""

from modules.project.domain.enums import (
    ProjectMilestoneStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectMilestoneState,
)


class ProjectMilestoneEngine:
    def achieve(self, row) -> None:
        if row.status not in {ProjectMilestoneStatus.PLANNED.value, ProjectMilestoneStatus.DELAYED.value}:
            raise InvalidProjectMilestoneState("Milestone not achievable")
        row.status = ProjectMilestoneStatus.ACHIEVED.value

    def delay(self, row) -> None:
        if row.status != ProjectMilestoneStatus.PLANNED.value:
            raise InvalidProjectMilestoneState("Only planned milestones can be delayed")
        row.status = ProjectMilestoneStatus.DELAYED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectMilestoneStatus.ACHIEVED.value, ProjectMilestoneStatus.CANCELLED.value}:
            raise InvalidProjectMilestoneState("Milestone already terminal")
        row.status = ProjectMilestoneStatus.CANCELLED.value

