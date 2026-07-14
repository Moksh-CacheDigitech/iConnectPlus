"""Goal lifecycle engine."""

from modules.hr.domain.enums import GoalStatus
from modules.hr.domain.exceptions import InvalidGoalState


class GoalEngine:
    def achieve(self, row) -> None:
        if row.status != GoalStatus.OPEN.value:
            raise InvalidGoalState("Only open goals can be achieved")
        row.status = GoalStatus.ACHIEVED.value

    def miss(self, row) -> None:
        if row.status != GoalStatus.OPEN.value:
            raise InvalidGoalState("Only open goals can be missed")
        row.status = GoalStatus.MISSED.value
