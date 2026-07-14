"""Offer lifecycle engine."""

from modules.recruitment.domain.enums import (
    OfferStatus,
)
from modules.recruitment.domain.exceptions import (
    InvalidOfferState,
)


class OfferEngine:
    def submit(self, row) -> None:
        if row.status != OfferStatus.DRAFT.value:
            raise InvalidOfferState("Only draft offers can be submitted")
        row.status = OfferStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != OfferStatus.SUBMITTED.value:
            raise InvalidOfferState("Only submitted offers can be approved")
        row.status = OfferStatus.APPROVED.value

    def send(self, row) -> None:
        if row.status != OfferStatus.APPROVED.value:
            raise InvalidOfferState("Only approved offers can be sent")
        row.status = OfferStatus.SENT.value

    def accept(self, row) -> None:
        if row.status != OfferStatus.SENT.value:
            raise InvalidOfferState("Only sent offers can be accepted")
        row.status = OfferStatus.ACCEPTED.value

    def reject(self, row) -> None:
        row.status = OfferStatus.REJECTED.value

    def expire(self, row) -> None:
        row.status = OfferStatus.EXPIRED.value

    def withdraw(self, row) -> None:
        row.status = OfferStatus.WITHDRAWN.value

    def cancel(self, row) -> None:
        row.status = OfferStatus.CANCELLED.value

