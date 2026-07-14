
"""Payroll domain enums per ERD_12 §11."""

from enum import Enum


class ActiveInactive(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PayrollPeriodStatus(str, Enum):
    OPEN = "open"
    PROCESSING = "processing"
    APPROVED = "approved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class SalaryStructureStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class TaxConfigurationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class EmployeeSalaryStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class PayrollRunStatus(str, Enum):
    DRAFT = "draft"
    CALCULATED = "calculated"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    PAID = "paid"
    CANCELLED = "cancelled"


class RunLineStatus(str, Enum):
    CALCULATED = "calculated"
    ADJUSTED = "adjusted"
    LOCKED = "locked"
    CANCELLED = "cancelled"


class PayslipStatus(str, Enum):
    GENERATED = "generated"
    ISSUED = "issued"
    VOID = "void"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    EMAILED = "emailed"
    VIEWED = "viewed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    UNPAID = "unpaid"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"


class BonusStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ReimbursementStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MANAGER_APPROVED = "manager_approved"
    FINANCE_APPROVED = "finance_approved"
    PAID = "paid"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LoanStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    CLOSED = "closed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LoanInstallmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    RECOVERED = "recovered"
    WAIVED = "waived"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class AdjustmentStatus(str, Enum):
    DRAFT = "draft"
    APPLIED = "applied"
    CANCELLED = "cancelled"


class PostingStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    POSTED = "posted"
    FAILED = "failed"
    REVERSED = "reversed"


class SummaryStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class PayEntityType(str, Enum):
    PAYROLL_RUN = "payroll_run"
    PAYSLIP = "payslip"
    EMPLOYEE_SALARY = "employee_salary"
    BONUS = "bonus"
    REIMBURSEMENT = "reimbursement"
    LOAN = "loan"
    PAYROLL_ADJUSTMENT = "payroll_adjustment"
    PAYROLL_POSTING = "payroll_posting"


CODE_PREFIXES: dict[PayEntityType, tuple[str, int]] = {
    PayEntityType.PAYROLL_RUN: ("PRUN-", 6),
    PayEntityType.PAYSLIP: ("PS-", 6),
    PayEntityType.EMPLOYEE_SALARY: ("ESAL-", 6),
    PayEntityType.BONUS: ("BON-", 6),
    PayEntityType.REIMBURSEMENT: ("REIM-", 6),
    PayEntityType.LOAN: ("LOAN-", 6),
    PayEntityType.PAYROLL_ADJUSTMENT: ("PADJ-", 6),
    PayEntityType.PAYROLL_POSTING: ("PPOST-", 6),
}
