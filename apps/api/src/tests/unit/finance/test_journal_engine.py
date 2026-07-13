"""Unit tests for journal engine."""


import pytest

from modules.finance.domain.exceptions import PeriodClosed, UnbalancedJournal
from modules.finance.service.engines.journal_engine import JournalEngine


class FakeLine:
    def __init__(self, debit: float, credit: float, is_deleted: bool = False) -> None:
        self.debit_amount = debit
        self.credit_amount = credit
        self.base_debit_amount = debit
        self.base_credit_amount = credit
        self.is_deleted = is_deleted


def test_journal_balancing_passes() -> None:
    engine = JournalEngine()
    lines = [FakeLine(100, 0), FakeLine(0, 100)]
    totals = engine.compute_totals(lines)
    assert totals.is_balanced
    engine.validate_balanced(totals)


def test_journal_balancing_fails() -> None:
    engine = JournalEngine()
    lines = [FakeLine(100, 0), FakeLine(0, 50)]
    totals = engine.compute_totals(lines)
    with pytest.raises(UnbalancedJournal):
        engine.validate_balanced(totals)


def test_minimum_lines_required() -> None:
    engine = JournalEngine()
    with pytest.raises(UnbalancedJournal):
        engine.validate_lines_count([FakeLine(10, 0)])


def test_exclusive_debit_credit() -> None:
    engine = JournalEngine()
    with pytest.raises(UnbalancedJournal):
        engine.validate_amounts(100, 50)


def test_period_hard_closed_blocks() -> None:
    engine = JournalEngine()

    class FakePeriod:
        status = "hard_closed"

    with pytest.raises(PeriodClosed):
        engine.validate_period_for_journal(FakePeriod(), "manual")
