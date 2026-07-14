"""Integration smoke: Payroll module imports and router mount."""

from modules.payroll.models import PayPayrollPeriod, PayPayrollRun, PayPayslip
from modules.payroll.router import payroll_router
from modules.payroll.service import (
    PayrollApplicationService,
    PayrollPeriodService,
    PayrollRunService,
)
from modules.payroll.service.engines import PayrollPeriodEngine, PayrollRunEngine


def test_payroll_models_importable():
    assert PayPayrollPeriod.__tablename__ == "pay_payroll_period"
    assert PayPayrollRun.__tablename__ == "pay_payroll_run"
    assert PayPayslip.__tablename__ == "pay_payslip"


def test_payroll_router_mounted():
    assert payroll_router.prefix == "/payroll"
    assert len(payroll_router.routes) > 20


def test_payroll_services_and_engines_importable():
    assert PayrollApplicationService is not None
    assert PayrollPeriodService is not None
    assert PayrollRunService is not None
    assert PayrollPeriodEngine is not None
    assert PayrollRunEngine is not None
