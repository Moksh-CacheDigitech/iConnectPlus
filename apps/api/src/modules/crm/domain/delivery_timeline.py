"""Committed delivery lead time, e.g. '16-18 weeks' from the customer PO date."""

from __future__ import annotations

import re
from datetime import date, timedelta

_WEEKS_RE = re.compile(r"(\d{1,3})\s*(?:(?:-|–|to)\s*(\d{1,3}))?\s*(?:weeks?|wks?|w)\b", re.IGNORECASE)


def parse_delivery_weeks(text: str | None) -> tuple[int, int] | None:
    """'16-18 weeks' → (16, 18); '6 weeks' → (6, 6); anything else → None."""
    if not text:
        return None
    match = _WEEKS_RE.search(text)
    if not match:
        return None
    low = int(match.group(1))
    high = int(match.group(2) or low)
    if low > high:
        low, high = high, low
    return low, high


def expected_delivery_date(start: date, weeks_max: int) -> date:
    """Last day of the final committed week counted from ``start``."""
    return start + timedelta(weeks=int(weeks_max))
