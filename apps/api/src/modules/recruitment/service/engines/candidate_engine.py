"""Candidate lifecycle engine."""

from modules.recruitment.domain.enums import (
    CandidateStatus,
)


class CandidateEngine:
    def advance_to_applied(self, row) -> None:
        row.status = CandidateStatus.APPLIED.value

    def advance_to_screening(self, row) -> None:
        row.status = CandidateStatus.SCREENING.value

    def advance_to_interview(self, row) -> None:
        row.status = CandidateStatus.INTERVIEW.value

    def advance_to_selected(self, row) -> None:
        row.status = CandidateStatus.SELECTED.value

    def advance_to_offered(self, row) -> None:
        row.status = CandidateStatus.OFFERED.value

    def mark_hired(self, row) -> None:
        row.status = CandidateStatus.HIRED.value

    def reject(self, row) -> None:
        row.status = CandidateStatus.REJECTED.value

    def hold(self, row) -> None:
        row.status = CandidateStatus.ON_HOLD.value

    def withdraw(self, row) -> None:
        row.status = CandidateStatus.WITHDRAWN.value

    def blacklist(self, row) -> None:
        row.status = CandidateStatus.BLACKLISTED.value

