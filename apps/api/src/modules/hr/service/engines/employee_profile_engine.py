"""EmployeeProfile lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive
from modules.hr.domain.exceptions import InvalidEmployeeProfileState


class EmployeeProfileEngine:
    def validate_writable(self, row) -> None:
        if row.status == ActiveInactive.INACTIVE.value:
            raise InvalidEmployeeProfileState("Inactive profile cannot be updated for ESS changes")
