"""Payroll application service facade."""

from sqlalchemy.orm import Session

from modules.payroll.service.adjustment_service import PayrollAdjustmentService
from modules.payroll.service.bonus_service import BonusService
from modules.payroll.service.deduction_type_service import DeductionTypeService
from modules.payroll.service.earning_type_service import EarningTypeService
from modules.payroll.service.employee_salary_service import EmployeeSalaryService
from modules.payroll.service.integration_service import PayrollIntegrationService
from modules.payroll.service.loan_service import LoanService
from modules.payroll.service.payroll_period_service import PayrollPeriodService
from modules.payroll.service.payroll_posting_service import PayrollPostingService
from modules.payroll.service.payroll_report_service import PayrollReportService
from modules.payroll.service.payroll_run_service import PayrollRunService
from modules.payroll.service.payslip_service import PayslipService
from modules.payroll.service.reimbursement_service import ReimbursementService
from modules.payroll.service.salary_component_service import SalaryComponentService
from modules.payroll.service.salary_structure_service import SalaryStructureService


class PayrollApplicationService:
    def __init__(self, db: Session) -> None:
        self.periods = PayrollPeriodService(db)
        self.structures = SalaryStructureService(db)
        self.components = SalaryComponentService(db)
        self.employee_salaries = EmployeeSalaryService(db)
        self.runs = PayrollRunService(db)
        self.payslips = PayslipService(db)
        self.bonuses = BonusService(db)
        self.reimbursements = ReimbursementService(db)
        self.loans = LoanService(db)
        self.postings = PayrollPostingService(db)
        self.reports = PayrollReportService(db)
        self.integration = PayrollIntegrationService(db)
        self.earning_types = EarningTypeService(db)
        self.deduction_types = DeductionTypeService(db)
        self.adjustments = PayrollAdjustmentService(db)
