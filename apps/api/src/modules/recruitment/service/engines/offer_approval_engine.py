"""OfferApproval lifecycle engine."""

from modules.recruitment.domain.enums import (
    OfferApprovalStatus,
)


class OfferApprovalEngine:
    def complete(self, row) -> None:
        row.status = OfferApprovalStatus.COMPLETED.value

    def skip(self, row) -> None:
        row.status = OfferApprovalStatus.SKIPPED.value

    def cancel(self, row) -> None:
        row.status = OfferApprovalStatus.CANCELLED.value

