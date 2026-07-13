"""Unit tests for sales discount and credit engines."""

from decimal import Decimal
from uuid import uuid4

import pytest

from modules.sales.domain.exceptions import CreditHoldError, CreditLimitExceeded
from modules.sales.service.engines.credit_check_engine import CreditCheckEngine
from modules.sales.service.engines.discount_engine import DiscountEngine


class _Rule:
    def __init__(
        self,
        discount_type,
        discount_value,
        *,
        requires_approval=False,
        max_discount_percent=None,
    ):
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.requires_approval = requires_approval
        self.max_discount_percent = max_discount_percent


class _Credit:
    def __init__(self, limit, used, available, hold=False, reason=None):
        self.customer_id = uuid4()
        self.credit_limit = limit
        self.credit_used = used
        self.credit_available = available
        self.credit_hold = hold
        self.credit_hold_reason = reason


def test_percent_discount_computes_amount() -> None:
    result = DiscountEngine().apply_discount(
        base_amount=Decimal("1000"),
        rule=_Rule("percent", 10),
    )
    assert result.discount_amount == Decimal("100.0000")
    assert result.applied_percent == Decimal("10")


def test_discount_over_max_requires_approval() -> None:
    result = DiscountEngine().apply_discount(
        base_amount=Decimal("1000"),
        rule=_Rule("percent", 20, max_discount_percent=10),
        discount_percent=Decimal("20"),
    )
    assert result.requires_approval is True


def test_credit_check_passes_within_limit() -> None:
    result = CreditCheckEngine().check(
        _Credit(10000, 2000, 8000),
        additional_amount=Decimal("1000"),
    )
    assert result.approved is True


def test_credit_check_raises_on_limit() -> None:
    with pytest.raises(CreditLimitExceeded):
        CreditCheckEngine().check(
            _Credit(5000, 4500, 500),
            additional_amount=Decimal("1000"),
        )


def test_credit_hold_raises() -> None:
    with pytest.raises(CreditHoldError):
        CreditCheckEngine().check(_Credit(5000, 0, 5000, hold=True, reason="Overdue"))


def test_recalculate_available() -> None:
    credit = _Credit(10000, 2500, 0)
    available = CreditCheckEngine().recalculate_available(credit)
    assert available == Decimal("7500")
    assert credit.credit_available == 7500.0
