"""Unit tests for payroll engines."""

from types import SimpleNamespace

from modules.payroll.service.engines import (
    BonusEngine,
    LoanEngine,
    PayrollPeriodEngine,
    PayrollRunEngine,
)


def test_payroll_period_processing():
    engine = PayrollPeriodEngine()
    row = SimpleNamespace(status="open")
    engine.start_processing(row)
    assert row.status == "processing"
    engine.approve(row)
    assert row.status == "approved"


def test_payroll_run_lifecycle():
    engine = PayrollRunEngine()
    row = SimpleNamespace(status="draft")
    engine.calculate(row)
    assert row.status == "calculated"
    engine.submit(row)
    engine.approve(row)
    assert row.status == "approved"


def test_bonus_submit_approve():
    engine = BonusEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    assert row.status == "approved"


def test_loan_flow():
    engine = LoanEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.activate(row)
    assert row.status == "active"
