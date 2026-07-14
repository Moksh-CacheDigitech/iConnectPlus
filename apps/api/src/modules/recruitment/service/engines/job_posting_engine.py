"""JobPosting lifecycle engine."""

from modules.recruitment.domain.enums import (
    JobPostingStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidJobPostingState,
)


class JobPostingEngine:
    def publish(self, row) -> None:
        if row.status not in {JobPostingStatus.DRAFT.value, JobPostingStatus.PAUSED.value}:
            raise InvalidJobPostingState("Posting not publishable")
        row.status = JobPostingStatus.PUBLISHED.value

    def pause(self, row) -> None:
        if row.status != JobPostingStatus.PUBLISHED.value:
            raise InvalidJobPostingState("Only published postings can be paused")
        row.status = JobPostingStatus.PAUSED.value

    def close(self, row) -> None:
        if row.status not in {JobPostingStatus.PUBLISHED.value, JobPostingStatus.PAUSED.value}:
            raise InvalidJobPostingState("Posting not closable")
        row.status = JobPostingStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status == JobPostingStatus.CANCELLED.value:
            raise InvalidJobPostingState("Posting already cancelled")
        row.status = JobPostingStatus.CANCELLED.value

