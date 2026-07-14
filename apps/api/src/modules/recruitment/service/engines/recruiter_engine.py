"""Recruiter lifecycle engine."""

from modules.recruitment.domain.enums import (
    ActiveInactive,
)


class RecruiterEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

