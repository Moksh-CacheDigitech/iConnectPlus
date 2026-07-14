"""ProjectPhase lifecycle engine."""

from modules.project.domain.enums import (
    ProjectPhaseStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectPhaseState,
)


class ProjectPhaseEngine:
    def activate(self, row) -> None:
        if row.status != ProjectPhaseStatus.PLANNED.value:
            raise InvalidProjectPhaseState("Only planned phases can activate")
        row.status = ProjectPhaseStatus.ACTIVE.value

    def complete(self, row) -> None:
        if row.status != ProjectPhaseStatus.ACTIVE.value:
            raise InvalidProjectPhaseState("Only active phases can complete")
        row.status = ProjectPhaseStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectPhaseStatus.COMPLETED.value, ProjectPhaseStatus.CANCELLED.value}:
            raise InvalidProjectPhaseState("Phase already terminal")
        row.status = ProjectPhaseStatus.CANCELLED.value

