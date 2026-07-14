"""Project value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProjectBudgetLine:
    budget_type: str
    budget_amount: Decimal
    currency_code: str


@dataclass(frozen=True)
class ProjectHealthSnapshot:
    health_status: str
    overdue_tasks: int
    budget_variance: Decimal | None = None
