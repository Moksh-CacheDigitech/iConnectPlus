"""Integration tests for journal to GL flow (unit-level engine chain)."""

from decimal import Decimal

from modules.finance.service.engines.journal_engine import JournalEngine


class Line:
    def __init__(self, d: float, c: float) -> None:
        self.debit_amount = d
        self.credit_amount = c
        self.base_debit_amount = d
        self.base_credit_amount = c
        self.is_deleted = False


def test_journal_to_gl_balance_invariant() -> None:
    """Balanced journal totals are prerequisite for GL posting."""
    engine = JournalEngine()
    lines = [Line(5000, 0), Line(0, 3000), Line(0, 2000)]
    totals = engine.compute_totals(lines)
    assert totals.total_debit == Decimal("5000")
    assert totals.total_credit == Decimal("5000")
    engine.validate_balanced(totals)
