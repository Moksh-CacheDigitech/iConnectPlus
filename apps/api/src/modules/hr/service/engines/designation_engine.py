"""Designation lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive
from modules.hr.domain.exceptions import InvalidDesignationState


class DesignationEngine:
    def validate_active(self, row) -> None:
        if row.status not in {"active", "inactive"}:
            raise InvalidDesignationState("Invalid designation status")

    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
