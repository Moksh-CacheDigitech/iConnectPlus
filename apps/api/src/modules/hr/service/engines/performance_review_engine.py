"""PerformanceReview lifecycle engine."""

from modules.hr.domain.enums import PerformanceReviewStatus
from modules.hr.domain.exceptions import InvalidPerformanceReviewState


class PerformanceReviewEngine:
    def start(self, row) -> None:
        if row.status != PerformanceReviewStatus.DRAFT.value:
            raise InvalidPerformanceReviewState("Only draft reviews can start")
        row.status = PerformanceReviewStatus.IN_PROGRESS.value

    def submit(self, row) -> None:
        if row.status not in {
            PerformanceReviewStatus.DRAFT.value,
            PerformanceReviewStatus.IN_PROGRESS.value,
        }:
            raise InvalidPerformanceReviewState("Review not submittable")
        row.status = PerformanceReviewStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != PerformanceReviewStatus.SUBMITTED.value:
            raise InvalidPerformanceReviewState("Only submitted reviews can be approved")
        row.status = PerformanceReviewStatus.APPROVED.value

    def close(self, row) -> None:
        if row.status != PerformanceReviewStatus.APPROVED.value:
            raise InvalidPerformanceReviewState("Only approved reviews can be closed")
        row.status = PerformanceReviewStatus.CLOSED.value
