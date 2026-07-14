"""Generator functions tail — merged into _gen_payroll_module.py by _assemble_payroll_gen.py"""


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    return f'''"""Payroll {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.payroll.models import {cls}
from modules.payroll.repository.base import PayScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class {name}Repository(PayScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_pay_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_pay_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> {cls}:
        row = {cls}(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> {cls} | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
'''


ENGINE_BODIES: dict[str, str] = {
    "PayrollPeriod": '''
class PayrollPeriodEngine:
    def open(self, row) -> None:
        if row.status not in {"open", "processing"}:
            raise InvalidPayrollPeriodState("Period not openable from current status")

    def start_processing(self, row) -> None:
        if row.status != PayrollPeriodStatus.OPEN.value:
            raise InvalidPayrollPeriodState("Only open periods can enter processing")
        row.status = PayrollPeriodStatus.PROCESSING.value

    def approve(self, row) -> None:
        if row.status != PayrollPeriodStatus.PROCESSING.value:
            raise InvalidPayrollPeriodState("Only processing periods can be approved")
        row.status = PayrollPeriodStatus.APPROVED.value

    def close(self, row) -> None:
        if row.status != PayrollPeriodStatus.APPROVED.value:
            raise InvalidPayrollPeriodState("Only approved periods can be closed")
        row.status = PayrollPeriodStatus.CLOSED.value
''',
    "SalaryStructure": '''
class SalaryStructureEngine:
    def activate(self, row) -> None:
        if row.status not in {SalaryStructureStatus.DRAFT.value, SalaryStructureStatus.INACTIVE.value}:
            raise InvalidSalaryStructureState("Structure not activatable")
        row.status = SalaryStructureStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        if row.status != SalaryStructureStatus.ACTIVE.value:
            raise InvalidSalaryStructureState("Only active structures can be deactivated")
        row.status = SalaryStructureStatus.INACTIVE.value
''',
    "SalaryComponent": '''
class SalaryComponentEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "SalaryStructureLine": '''
class SalaryStructureLineEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "EmployeeSalary": '''
class EmployeeSalaryEngine:
    def activate(self, row) -> None:
        if row.status not in {EmployeeSalaryStatus.DRAFT.value}:
            raise InvalidEmployeeSalaryState("Only draft salary can be activated")
        row.status = EmployeeSalaryStatus.ACTIVE.value

    def end(self, row) -> None:
        if row.status != EmployeeSalaryStatus.ACTIVE.value:
            raise InvalidEmployeeSalaryState("Only active salary can be ended")
        row.status = EmployeeSalaryStatus.ENDED.value
''',
    "EmployeeSalaryComponent": '''
class EmployeeSalaryComponentEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "EarningType": '''
class EarningTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "DeductionType": '''
class DeductionTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "PayrollRun": '''
class PayrollRunEngine:
    def calculate(self, row) -> None:
        if row.status not in {PayrollRunStatus.DRAFT.value}:
            raise InvalidPayrollRunState("Only draft runs can be calculated")
        row.status = PayrollRunStatus.CALCULATED.value

    def submit(self, row) -> None:
        if row.status != PayrollRunStatus.CALCULATED.value:
            raise InvalidPayrollRunState("Only calculated runs can be submitted")
        row.status = PayrollRunStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != PayrollRunStatus.SUBMITTED.value:
            raise InvalidPayrollRunState("Only submitted runs can be approved")
        row.status = PayrollRunStatus.APPROVED.value

    def mark_posted(self, row) -> None:
        if row.status != PayrollRunStatus.APPROVED.value:
            raise InvalidPayrollRunState("Only approved runs can be posted")
        row.status = PayrollRunStatus.POSTED.value

    def mark_paid(self, row) -> None:
        if row.status != PayrollRunStatus.POSTED.value:
            raise InvalidPayrollRunState("Only posted runs can be marked paid")
        row.status = PayrollRunStatus.PAID.value
''',
    "PayrollRunLine": '''
class PayrollRunLineEngine:
    def adjust(self, row) -> None:
        if row.status not in {RunLineStatus.CALCULATED.value, RunLineStatus.ADJUSTED.value}:
            raise InvalidPayrollRunLineState("Line not adjustable")
        row.status = RunLineStatus.ADJUSTED.value

    def lock(self, row) -> None:
        if row.status == RunLineStatus.LOCKED.value:
            raise InvalidPayrollRunLineState("Line already locked")
        row.status = RunLineStatus.LOCKED.value
''',
    "Payslip": '''
class PayslipEngine:
    def issue(self, row) -> None:
        if row.status != PayslipStatus.GENERATED.value:
            raise InvalidPayslipState("Only generated payslips can be issued")
        row.status = PayslipStatus.ISSUED.value

    def void(self, row) -> None:
        if row.status == PayslipStatus.VOID.value:
            raise InvalidPayslipState("Payslip already void")
        row.status = PayslipStatus.VOID.value
''',
    "TaxConfiguration": '''
class TaxConfigurationEngine:
    def activate(self, row) -> None:
        if row.status != TaxConfigurationStatus.DRAFT.value:
            raise InvalidTaxConfigurationState("Only draft tax config can activate")
        row.status = TaxConfigurationStatus.ACTIVE.value

    def archive(self, row) -> None:
        if row.status != TaxConfigurationStatus.ACTIVE.value:
            raise InvalidTaxConfigurationState("Only active tax config can archive")
        row.status = TaxConfigurationStatus.ARCHIVED.value
''',
    "StatutoryContribution": '''
class StatutoryContributionEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "Bonus": '''
class BonusEngine:
    def submit(self, row) -> None:
        if row.status != BonusStatus.DRAFT.value:
            raise InvalidBonusState("Only draft bonus can be submitted")
        row.status = BonusStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != BonusStatus.SUBMITTED.value:
            raise InvalidBonusState("Only submitted bonus can be approved")
        row.status = BonusStatus.APPROVED.value

    def mark_paid(self, row) -> None:
        if row.status != BonusStatus.APPROVED.value:
            raise InvalidBonusState("Only approved bonus can be paid")
        row.status = BonusStatus.PAID.value
''',
    "Reimbursement": '''
class ReimbursementEngine:
    def submit(self, row) -> None:
        if row.status != ReimbursementStatus.DRAFT.value:
            raise InvalidReimbursementState("Only draft reimbursement can be submitted")
        row.status = ReimbursementStatus.SUBMITTED.value

    def manager_approve(self, row) -> None:
        if row.status != ReimbursementStatus.SUBMITTED.value:
            raise InvalidReimbursementState("Only submitted reimbursement can be manager approved")
        row.status = ReimbursementStatus.MANAGER_APPROVED.value

    def finance_approve(self, row) -> None:
        if row.status != ReimbursementStatus.MANAGER_APPROVED.value:
            raise InvalidReimbursementState("Manager approval required")
        row.status = ReimbursementStatus.FINANCE_APPROVED.value
''',
    "Loan": '''
class LoanEngine:
    def submit(self, row) -> None:
        if row.status != LoanStatus.DRAFT.value:
            raise InvalidLoanState("Only draft loans can be submitted")
        row.status = LoanStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != LoanStatus.SUBMITTED.value:
            raise InvalidLoanState("Only submitted loans can be approved")
        row.status = LoanStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != LoanStatus.APPROVED.value:
            raise InvalidLoanState("Only approved loans can activate")
        row.status = LoanStatus.ACTIVE.value

    def close(self, row) -> None:
        if row.status != LoanStatus.ACTIVE.value:
            raise InvalidLoanState("Only active loans can close")
        row.status = LoanStatus.CLOSED.value
''',
    "LoanInstallment": '''
class LoanInstallmentEngine:
    def recover(self, row) -> None:
        if row.status != LoanInstallmentStatus.SCHEDULED.value:
            raise InvalidLoanInstallmentState("Only scheduled installments can be recovered")
        row.status = LoanInstallmentStatus.RECOVERED.value

    def waive(self, row) -> None:
        if row.status not in {LoanInstallmentStatus.SCHEDULED.value, LoanInstallmentStatus.OVERDUE.value}:
            raise InvalidLoanInstallmentState("Installment cannot be waived")
        row.status = LoanInstallmentStatus.WAIVED.value
''',
    "PayrollAdjustment": '''
class PayrollAdjustmentEngine:
    def apply(self, row) -> None:
        if row.status != AdjustmentStatus.DRAFT.value:
            raise InvalidPayrollAdjustmentState("Only draft adjustments can be applied")
        row.status = AdjustmentStatus.APPLIED.value
''',
    "PayrollPosting": '''
class PayrollPostingEngine:
    def submit(self, row) -> None:
        if row.status != PostingStatus.DRAFT.value:
            raise InvalidPayrollPostingState("Only draft posting can be submitted")
        row.status = PostingStatus.SUBMITTED.value

    def mark_posted(self, row) -> None:
        if row.status != PostingStatus.SUBMITTED.value:
            raise InvalidPayrollPostingState("Only submitted posting can post")
        row.status = PostingStatus.POSTED.value

    def mark_failed(self, row, message: str) -> None:
        row.status = PostingStatus.FAILED.value
        row.error_message = message
''',
    "PayrollSummary": '''
class PayrollSummaryEngine:
    def finalize(self, row) -> None:
        if row.status != SummaryStatus.DRAFT.value:
            raise InvalidPayrollSummaryState("Only draft summaries can finalize")
        row.status = SummaryStatus.FINALIZED.value
''',
}

ENGINE_IMPORTS = '''
from modules.payroll.domain.enums import (
    ActiveInactive,
    AdjustmentStatus,
    BonusStatus,
    EmployeeSalaryStatus,
    LoanInstallmentStatus,
    LoanStatus,
    PayrollPeriodStatus,
    PayrollRunStatus,
    PayslipStatus,
    PostingStatus,
    ReimbursementStatus,
    RunLineStatus,
    SalaryStructureStatus,
    SummaryStatus,
    TaxConfigurationStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidBonusState,
    InvalidDeductionTypeState,
    InvalidEarningTypeState,
    InvalidEmployeeSalaryComponentState,
    InvalidEmployeeSalaryState,
    InvalidLoanInstallmentState,
    InvalidLoanState,
    InvalidPayrollAdjustmentState,
    InvalidPayrollPeriodState,
    InvalidPayrollPostingState,
    InvalidPayrollRunLineState,
    InvalidPayrollRunState,
    InvalidPayrollSummaryState,
    InvalidPayslipState,
    InvalidReimbursementState,
    InvalidSalaryComponentState,
    InvalidSalaryStructureLineState,
    InvalidSalaryStructureState,
    InvalidStatutoryContributionState,
    InvalidTaxConfigurationState,
)
'''

ENGINE_FILE_MAP = {
    "PayrollPeriod": "payroll_period",
    "SalaryStructure": "salary_structure",
    "SalaryComponent": "salary_component",
    "SalaryStructureLine": "salary_structure_line",
    "EmployeeSalary": "employee_salary",
    "EmployeeSalaryComponent": "employee_salary_component",
    "EarningType": "earning_type",
    "DeductionType": "deduction_type",
    "PayrollRun": "payroll_run",
    "PayrollRunLine": "payroll_run_line",
    "Payslip": "payslip",
    "TaxConfiguration": "tax_configuration",
    "StatutoryContribution": "statutory_contribution",
    "Bonus": "bonus",
    "Reimbursement": "reimbursement",
    "Loan": "loan",
    "LoanInstallment": "loan_installment",
    "PayrollAdjustment": "payroll_adjustment",
    "PayrollPosting": "payroll_posting",
    "PayrollSummary": "payroll_summary",
}
