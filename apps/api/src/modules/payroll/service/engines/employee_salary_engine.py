"""EmployeeSalary lifecycle engine."""

from modules.payroll.domain.enums import (
    EmployeeSalaryStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidEmployeeSalaryState,
)


class EmployeeSalaryEngine:
    def activate(self, row) -> None:
        if row.status not in {EmployeeSalaryStatus.DRAFT.value}:
            raise InvalidEmployeeSalaryState("Only draft salary can be activated")
        row.status = EmployeeSalaryStatus.ACTIVE.value

    def end(self, row) -> None:
        if row.status != EmployeeSalaryStatus.ACTIVE.value:
            raise InvalidEmployeeSalaryState("Only active salary can be ended")
        row.status = EmployeeSalaryStatus.ENDED.value

