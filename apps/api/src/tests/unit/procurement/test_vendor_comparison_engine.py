"""Unit tests for vendor comparison engine."""

from uuid import uuid4

from modules.procurement.service.engines.vendor_comparison_engine import VendorComparisonEngine


class _Quote:
    def __init__(self, total, delivery_days, status="submitted"):
        self.id = uuid4()
        self.total_amount = total
        self.delivery_days = delivery_days
        self.status = status
        self.is_deleted = False


def test_comparison_picks_best_price_and_delivery() -> None:
    cheap_slow = _Quote(100, 30)
    expensive_fast = _Quote(200, 5)
    mid = _Quote(150, 10)
    result = VendorComparisonEngine().compare([cheap_slow, expensive_fast, mid])
    assert result.best_price_quotation_id == cheap_slow.id
    assert result.best_delivery_quotation_id == expensive_fast.id
    assert result.best_overall_quotation_id is not None
    assert len(result.score_breakdown["quotations"]) == 3


def test_comparison_empty() -> None:
    result = VendorComparisonEngine().compare([])
    assert result.best_price_quotation_id is None
