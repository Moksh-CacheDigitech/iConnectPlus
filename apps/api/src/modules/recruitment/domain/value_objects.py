
"""Recruitment value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateIdentity:
    first_name: str
    last_name: str
    email: str
    mobile: str | None = None


@dataclass(frozen=True)
class OfferCompensation:
    offered_ctc: float | None
    currency_code: str
