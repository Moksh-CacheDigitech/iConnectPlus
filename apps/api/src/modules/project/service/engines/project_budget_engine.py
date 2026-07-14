"""ProjectBudget lifecycle engine."""

from modules.project.domain.enums import (
    ProjectBudgetStatus,
)
from modules.project.domain.exceptions import (
    InvalidProjectBudgetState,
)


class ProjectBudgetEngine:
    def submit(self, row) -> None:
        if row.status != ProjectBudgetStatus.DRAFT.value:
            raise InvalidProjectBudgetState("Only draft budgets can be submitted")
        row.status = ProjectBudgetStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProjectBudgetStatus.SUBMITTED.value:
            raise InvalidProjectBudgetState("Only submitted budgets can be approved")
        row.status = ProjectBudgetStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != ProjectBudgetStatus.APPROVED.value:
            raise InvalidProjectBudgetState("Only approved budgets can activate")
        row.status = ProjectBudgetStatus.ACTIVE.value

    def close(self, row) -> None:
        if row.status != ProjectBudgetStatus.ACTIVE.value:
            raise InvalidProjectBudgetState("Only active budgets can close")
        row.status = ProjectBudgetStatus.CLOSED.value

    def reject(self, row) -> None:
        if row.status != ProjectBudgetStatus.SUBMITTED.value:
            raise InvalidProjectBudgetState("Only submitted budgets can be rejected")
        row.status = ProjectBudgetStatus.REJECTED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectBudgetStatus.CLOSED.value, ProjectBudgetStatus.CANCELLED.value}:
            raise InvalidProjectBudgetState("Budget already terminal")
        row.status = ProjectBudgetStatus.CANCELLED.value

