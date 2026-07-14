"""ResourcePlan lifecycle engine."""

from modules.project.domain.enums import (
    ResourcePlanStatus,
)
from modules.project.domain.exceptions import (
    InvalidResourcePlanState,
)


class ResourcePlanEngine:
    def activate(self, row) -> None:
        if row.status != ResourcePlanStatus.DRAFT.value:
            raise InvalidResourcePlanState("Only draft plans can activate")
        row.status = ResourcePlanStatus.ACTIVE.value

    def close(self, row) -> None:
        if row.status != ResourcePlanStatus.ACTIVE.value:
            raise InvalidResourcePlanState("Only active plans can close")
        row.status = ResourcePlanStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ResourcePlanStatus.CLOSED.value, ResourcePlanStatus.CANCELLED.value}:
            raise InvalidResourcePlanState("Plan already terminal")
        row.status = ResourcePlanStatus.CANCELLED.value

