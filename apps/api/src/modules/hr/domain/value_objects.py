"""HR value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LeaveDays:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Leave days must be positive")


@dataclass(frozen=True)
class RatingScore:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1 or self.value > 5:
            raise ValueError("Rating must be 1-5")
