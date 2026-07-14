"""Shift lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive


class ShiftEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
