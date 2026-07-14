"""ProjectCost lifecycle engine."""

from modules.project.domain.enums import (
    ProjectCostStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectCostState,
)


class ProjectCostEngine:
    def post(self, row) -> None:
        if row.status != ProjectCostStatus.DRAFT.value:
            raise InvalidProjectCostState("Only draft costs can be posted")
        row.status = ProjectCostStatus.POSTED.value

    def fail(self, row) -> None:
        if row.status != ProjectCostStatus.DRAFT.value:
            raise InvalidProjectCostState("Only draft costs can fail")
        row.status = ProjectCostStatus.FAILED.value

    def reverse(self, row) -> None:
        if row.status != ProjectCostStatus.POSTED.value:
            raise InvalidProjectCostState("Only posted costs can be reversed")
        row.status = ProjectCostStatus.REVERSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectCostStatus.POSTED.value, ProjectCostStatus.CANCELLED.value}:
            raise InvalidProjectCostState("Cost already terminal")
        row.status = ProjectCostStatus.CANCELLED.value

