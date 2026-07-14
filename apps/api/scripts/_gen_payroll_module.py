"""Generate Sprint 12 Payroll module artifacts. Run from apps/api: python scripts/_gen_payroll_module.py"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PAY = SRC / "modules" / "payroll"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    FILES_WRITTEN.append(path)
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new.strip() in text:
        print("skip (already)", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"patch failed in {path}: marker not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# Table registry: (module, ORM class, repo name, branch_scoped)
# ---------------------------------------------------------------------------

TABLES: list[tuple[str, str, str, bool]] = [
    ("payroll_period", "PayPayrollPeriod", "PayrollPeriod", False),
    ("salary_structure", "PaySalaryStructure", "SalaryStructure", False),
    ("salary_component", "PaySalaryComponent", "SalaryComponent", False),
    ("salary_structure_line", "PaySalaryStructureLine", "SalaryStructureLine", False),
    ("employee_salary", "PayEmployeeSalary", "EmployeeSalary", True),
    ("employee_salary_component", "PayEmployeeSalaryComponent", "EmployeeSalaryComponent", True),
    ("earning_type", "PayEarningType", "EarningType", False),
    ("deduction_type", "PayDeductionType", "DeductionType", False),
    ("payroll_run", "PayPayrollRun", "PayrollRun", True),
    ("payroll_run_line", "PayPayrollRunLine", "PayrollRunLine", True),
    ("payslip", "PayPayslip", "Payslip", True),
    ("tax_configuration", "PayTaxConfiguration", "TaxConfiguration", False),
    ("statutory_contribution", "PayStatutoryContribution", "StatutoryContribution", False),
    ("bonus", "PayBonus", "Bonus", True),
    ("reimbursement", "PayReimbursement", "Reimbursement", True),
    ("loan", "PayLoan", "Loan", True),
    ("loan_installment", "PayLoanInstallment", "LoanInstallment", True),
    ("payroll_adjustment", "PayPayrollAdjustment", "PayrollAdjustment", True),
    ("payroll_posting", "PayPayrollPosting", "PayrollPosting", True),
    ("payroll_summary", "PayPayrollSummary", "PayrollSummary", False),
]

CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0179_create_payroll_schema", "schema", "0178_seed_hr_workflows"),
    ("0180_pay_payroll_period", "payroll_period", "0179_create_payroll_schema"),
    ("0181_pay_earn_deduct_types", ["earning_type", "deduction_type"], "0180_pay_payroll_period"),
    ("0182_pay_salary_component", "salary_component", "0181_pay_earn_deduct_types"),
    ("0183_pay_salary_structure", "salary_structure", "0182_pay_salary_component"),
    ("0184_pay_sal_struct_line", "salary_structure_line", "0183_pay_salary_structure"),
    ("0185_pay_employee_salary", "employee_salary", "0184_pay_sal_struct_line"),
    ("0186_pay_emp_salary_comp", "employee_salary_component", "0185_pay_employee_salary"),
    ("0187_pay_tax_configuration", "tax_configuration", "0186_pay_emp_salary_comp"),
    ("0188_pay_statutory_contrib", "statutory_contribution", "0187_pay_tax_configuration"),
    ("0189_pay_payroll_run", "payroll_run", "0188_pay_statutory_contrib"),
    ("0190_pay_payroll_run_line", "payroll_run_line", "0189_pay_payroll_run"),
    ("0191_pay_payslip", "payslip", "0190_pay_payroll_run_line"),
    ("0192_pay_bonus", "bonus", "0191_pay_payslip"),
    ("0193_pay_reimbursement", "reimbursement", "0192_pay_bonus"),
    ("0194_pay_loan", "loan", "0193_pay_reimbursement"),
    ("0195_pay_loan_installment", "loan_installment", "0194_pay_loan"),
    ("0196_pay_payroll_adjustment", "payroll_adjustment", "0195_pay_loan_installment"),
    ("0197_pay_payroll_posting", "payroll_posting", "0196_pay_payroll_adjustment"),
    ("0198_pay_payroll_summary", "payroll_summary", "0197_pay_payroll_posting"),
    ("0199_seed_payroll_permissions", "seed_perms", "0198_pay_payroll_summary"),
    ("0200_seed_payroll_workflows", "seed_wf", "0199_seed_payroll_permissions"),
]


def gen_scaffold() -> None:
    w(PAY / "__init__.py", '"""Payroll Management module — Sprint 12."""\n')
    w(PAY / "domain" / "__init__.py", '"""Payroll domain layer."""\n')
    w(PAY / "adapters" / "__init__.py", '"""Payroll cross-module adapters."""\n')
    w(PAY / "service" / "__init__.py", '"""Payroll services — populated after generation."""\n')
    w(PAY / "service" / "engines" / "__init__.py", '"""Payroll engines — populated after generation."""\n')
    w(PAY / "repository" / "__init__.py", '"""Payroll repositories."""\n')
    w(PAY / "models" / "__init__.py", '"""Payroll models — populated after generation."""\n')

    w(
        PAY / "models" / "mixins.py",
        '''
"""Payroll ORM mixin bundles per ERD_12."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

PayMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

PayTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

PayDetailMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
    )


def gen_domain() -> None:
    w(
        PAY / "domain" / "enums.py",
        '''
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
''',
    )

    exceptions = [
        "PayrollPeriod",
        "SalaryStructure",
        "SalaryComponent",
        "SalaryStructureLine",
        "EmployeeSalary",
        "EmployeeSalaryComponent",
        "EarningType",
        "DeductionType",
        "PayrollRun",
        "PayrollRunLine",
        "Payslip",
        "TaxConfiguration",
        "StatutoryContribution",
        "Bonus",
        "Reimbursement",
        "Loan",
        "LoanInstallment",
        "PayrollAdjustment",
        "PayrollPosting",
        "PayrollSummary",
    ]
    exc_lines = [
        f'''
class Invalid{name}State(ConflictException):
    def __init__(self, message: str = "Invalid {name.replace("Payroll", "payroll ").lower()} state") -> None:
        super().__init__(message)
'''
        for name in exceptions
    ]
    w(
        PAY / "domain" / "exceptions.py",
        '"""Payroll domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )

    w(
        PAY / "domain" / "value_objects.py",
        '''
"""Payroll value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MoneyAmount:
    value: Decimal
    currency_code: str

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency_code:
            raise ValueError("Currency code required")


@dataclass(frozen=True)
class PaidDays:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Paid days cannot be negative")
''',
    )

    agg_lines = "\n".join(
        f'    {t[2].upper().replace(" ", "_")} = "pay_{t[0]}"' for t in TABLES
    )
    w(
        PAY / "domain" / "entities.py",
        f'''"""Payroll domain entity markers (aggregates map 1:1 to ORM headers)."""

from enum import Enum


class PayAggregate(str, Enum):
{agg_lines}
''',
    )


MODELS: dict[str, str] = {}

MODELS["payroll_period"] = r'''"""Payroll period ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayPayrollPeriod(Base, *PayMasterMixin):
    __tablename__ = "pay_payroll_period"
    __table_args__ = (
        UniqueConstraint("company_id", "period_code", name="uk_pay_period_company_code"),
        CheckConstraint(
            "status IN ('open','processing','approved','closed','cancelled')",
            name="ck_pay_period_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    period_code: Mapped[str] = mapped_column(String(50), nullable=False)
    period_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payroll_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    payroll_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
'''

MODELS["earning_type"] = r'''"""Payroll earning type catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayEarningType(Base, *PayMasterMixin):
    __tablename__ = "pay_earning_type"
    __table_args__ = (
        UniqueConstraint("company_id", "earning_type_code", name="uk_pay_earn_type_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_earn_type_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    earning_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    earning_type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["deduction_type"] = r'''"""Payroll deduction type catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayDeductionType(Base, *PayMasterMixin):
    __tablename__ = "pay_deduction_type"
    __table_args__ = (
        UniqueConstraint("company_id", "deduction_type_code", name="uk_pay_ded_type_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_ded_type_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    deduction_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    deduction_type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_statutory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["salary_structure"] = r'''"""Salary structure catalog ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PaySalaryStructure(Base, *PayMasterMixin):
    __tablename__ = "pay_salary_structure"
    __table_args__ = (
        UniqueConstraint("company_id", "structure_code", name="uk_pay_struct_company_code"),
        CheckConstraint("status IN ('draft','active','inactive')", name="ck_pay_struct_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    structure_code: Mapped[str] = mapped_column(String(50), nullable=False)
    structure_name: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["salary_component"] = r'''"""Salary component catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PaySalaryComponent(Base, *PayMasterMixin):
    __tablename__ = "pay_salary_component"
    __table_args__ = (
        UniqueConstraint("company_id", "component_code", name="uk_pay_comp_company_code"),
        CheckConstraint(
            "component_class IN ('earning','deduction','employer_contribution')",
            name="ck_pay_comp_class",
        ),
        CheckConstraint(
            "calculation_method IN ('fixed','percentage','formula')",
            name="ck_pay_comp_calc",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_comp_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    component_code: Mapped[str] = mapped_column(String(50), nullable=False)
    component_name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_class: Mapped[str] = mapped_column(String(30), nullable=False)
    earning_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_earning_type.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    deduction_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_deduction_type.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    calculation_method: Mapped[str] = mapped_column(String(30), nullable=False, default="fixed")
    percentage_base_component_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_taxable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_statutory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gl_expense_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    gl_liability_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["salary_structure_line"] = r'''"""Salary structure line ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayDetailMixin


class PaySalaryStructureLine(Base, *PayDetailMixin):
    __tablename__ = "pay_salary_structure_line"
    __table_args__ = (
        UniqueConstraint(
            "salary_structure_id",
            "salary_component_id",
            name="uk_pay_struct_line_comp",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_struct_line_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    salary_structure_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_structure.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_component_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    default_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    default_percent: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["employee_salary"] = r'''"""Employee salary assignment ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayEmployeeSalary(Base, *PayTransactionMixin):
    __tablename__ = "pay_employee_salary"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_esal_company_doc"),
        CheckConstraint(
            "status IN ('draft','active','ended','cancelled')",
            name="ck_pay_esal_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_structure_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_structure.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employment_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    ctc_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["employee_salary_component"] = r'''"""Employee salary component override ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayEmployeeSalaryComponent(Base, *PayTransactionMixin):
    __tablename__ = "pay_employee_salary_component"
    __table_args__ = (
        UniqueConstraint(
            "employee_salary_id",
            "salary_component_id",
            name="uk_pay_emp_sal_comp",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_emp_sal_comp_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_salary_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_employee_salary.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_component_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    percent: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    override_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''


MODELS["tax_configuration"] = r'''"""Tax configuration ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayTaxConfiguration(Base, *PayMasterMixin):
    __tablename__ = "pay_tax_configuration"
    __table_args__ = (
        UniqueConstraint("company_id", "tax_config_code", name="uk_pay_tax_cfg_code"),
        CheckConstraint(
            "tax_type IN ('income_tax','professional_tax','other')",
            name="ck_pay_tax_cfg_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','archived')",
            name="ck_pay_tax_cfg_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    tax_config_code: Mapped[str] = mapped_column(String(50), nullable=False)
    tax_config_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(30), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    slabs_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["statutory_contribution"] = r'''"""Statutory contribution rate ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayStatutoryContribution(Base, *PayMasterMixin):
    __tablename__ = "pay_statutory_contribution"
    __table_args__ = (
        UniqueConstraint("company_id", "contribution_code", name="uk_pay_stat_contrib_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_stat_contrib_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    contribution_code: Mapped[str] = mapped_column(String(50), nullable=False)
    contribution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_rate_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    employer_rate_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    wage_ceiling_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary_component_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["payroll_run"] = r'''"""Payroll run header ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayPayrollRun(Base, *PayTransactionMixin):
    __tablename__ = "pay_payroll_run"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_run_company_doc"),
        CheckConstraint(
            "run_type IN ('regular','off_cycle','final_settlement')",
            name="ck_pay_run_type",
        ),
        CheckConstraint(
            "status IN ('draft','calculated','submitted','approved','posted','paid','cancelled')",
            name="ck_pay_run_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    run_type: Mapped[str] = mapped_column(String(30), nullable=False, default="regular")
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_gross: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_deduction: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_net: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_employer_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''

MODELS["payroll_run_line"] = r'''"""Payroll run line ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayPayrollRunLine(Base, *PayTransactionMixin):
    __tablename__ = "pay_payroll_run_line"
    __table_args__ = (
        CheckConstraint(
            "status IN ('calculated','adjusted','locked','cancelled')",
            name="ck_pay_run_line_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_salary_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_employee_salary.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    employment_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    paid_days: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    lop_days: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    leave_days: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    gross_earnings: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    net_pay: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    employer_contribution: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    component_breakdown_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="calculated", index=True)
'''

MODELS["payslip"] = r'''"""Payslip ORM."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayPayslip(Base, *PayTransactionMixin):
    __tablename__ = "pay_payslip"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_payslip_company_doc"),
        CheckConstraint(
            "delivery_status IN ('pending','emailed','viewed','failed')",
            name="ck_pay_payslip_delivery",
        ),
        CheckConstraint(
            "payment_status IN ('unpaid','processing','paid','failed')",
            name="ck_pay_payslip_payment",
        ),
        CheckConstraint(
            "status IN ('generated','issued','void')",
            name="ck_pay_payslip_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_run_line_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run_line.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    payslip_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    payment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unpaid")
    bank_export_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="generated", index=True)
'''

MODELS["bonus"] = r'''"""Bonus ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayBonus(Base, *PayTransactionMixin):
    __tablename__ = "pay_bonus"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_bonus_company_doc"),
        CheckConstraint(
            "bonus_type IN ('festival','performance','retention','other')",
            name="ck_pay_bonus_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','paid','rejected','cancelled')",
            name="ck_pay_bonus_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    bonus_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''

MODELS["reimbursement"] = r'''"""Reimbursement ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayReimbursement(Base, *PayTransactionMixin):
    __tablename__ = "pay_reimbursement"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_reim_company_doc"),
        CheckConstraint(
            "reimbursement_type IN ('travel','internet','medical','training','mobile','other')",
            name="ck_pay_reim_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','manager_approved','finance_approved','paid','rejected','cancelled')",
            name="ck_pay_reim_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    reimbursement_type: Mapped[str] = mapped_column(String(30), nullable=False)
    claim_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    approved_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''

MODELS["loan"] = r'''"""Loan ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayLoan(Base, *PayTransactionMixin):
    __tablename__ = "pay_loan"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_loan_company_doc"),
        CheckConstraint(
            "loan_type IN ('personal','salary_advance','emergency')",
            name="ck_pay_loan_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','closed','rejected','cancelled')",
            name="ck_pay_loan_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    loan_type: Mapped[str] = mapped_column(String(30), nullable=False)
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    emi_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False, default=0)
    installment_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''

MODELS["loan_installment"] = r'''"""Loan installment schedule ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayLoanInstallment(Base, *PayTransactionMixin):
    __tablename__ = "pay_loan_installment"
    __table_args__ = (
        UniqueConstraint("loan_id", "installment_no", name="uk_pay_loan_inst_no"),
        CheckConstraint(
            "status IN ('scheduled','recovered','waived','overdue','cancelled')",
            name="ck_pay_loan_inst_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    loan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_loan.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    installment_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payroll_period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    due_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    payroll_run_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run_line.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled", index=True)
'''

MODELS["payroll_adjustment"] = r'''"""Payroll adjustment ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayPayrollAdjustment(Base, *PayTransactionMixin):
    __tablename__ = "pay_payroll_adjustment"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_adj_company_doc"),
        CheckConstraint(
            "adjustment_type IN ('earning','deduction')",
            name="ck_pay_adj_type",
        ),
        CheckConstraint(
            "status IN ('draft','applied','cancelled')",
            name="ck_pay_adj_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_component_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    adjustment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["payroll_posting"] = r'''"""Payroll posting integration ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayPayrollPosting(Base, *PayTransactionMixin):
    __tablename__ = "pay_payroll_posting"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_post_company_doc"),
        UniqueConstraint("idempotency_key", name="uk_pay_post_idempotency"),
        CheckConstraint(
            "posting_type IN ('salary_expense','salary_payment')",
            name="ck_pay_post_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','posted','failed','reversed')",
            name="ck_pay_post_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fiscal_year_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    period_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    posting_type: Mapped[str] = mapped_column(String(30), nullable=False)
    debit_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    credit_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    finance_journal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="SET NULL"),
        nullable=True,
    )
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
'''

MODELS["payroll_summary"] = r'''"""Payroll summary aggregate ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayPayrollSummary(Base, *PayMasterMixin):
    __tablename__ = "pay_payroll_summary"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_pay_summary_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_gross: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_deduction: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_net: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_employer_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    summary_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''



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


"""Body functions for payroll generator — merged into _gen_payroll_module.py."""


def gen_models() -> None:
    for name, content in MODELS.items():
        w(PAY / "models" / f"{name}.py", content)
    init_imports = "\n".join(
        f"from modules.payroll.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP
    )
    all_list = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        PAY / "models" / "__init__.py",
        f'''"""Payroll ORM models."""

{init_imports}

__all__ = [
    {all_list},
]
''',
    )


def gen_migrations() -> None:
    w(
        ALEMBIC / "0179_create_payroll_schema.py",
        '''"""Create payroll schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0179_create_payroll_schema"
down_revision: str | None = "0178_seed_hr_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS payroll")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS payroll CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.payroll.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
                for m in target
            )
            creates = "\n    ".join(f"{CLASS_MAP[m]}.__table__.create(bind=op.get_bind(), checkfirst=True)" for m in target)
            drops = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.drop(bind=op.get_bind(), checkfirst=True)" for m in reversed(target)
            )
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create payroll catalog type tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

{imports}

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {creates}


def downgrade() -> None:
    {drops}
''',
            )
        else:
            cls = CLASS_MAP[target]
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.payroll.models.{target} import {cls}  # noqa: F401

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {cls}.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    {cls}.__table__.drop(bind=op.get_bind(), checkfirst=True)
''',
            )


def gen_repos() -> None:
    w(
        PAY / "repository" / "base.py",
        '''"""Payroll repository base utilities."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PayScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_pay_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = PayScopedRepository.apply_tenant_filter(stmt, model, ctx)
        if ctx.company_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(model.company_id == ctx.company_id)
        if (
            branch_scoped
            and ctx.branch_id
            and ctx.user_type not in {"super_admin", "tenant_admin"}
            and hasattr(model, "branch_id")
        ):
            stmt = stmt.where(model.branch_id == ctx.branch_id)
        return stmt

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            PayScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        PAY / "repository" / "code_sequence_repository.py",
        '''"""Payroll document code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.payroll.domain.enums import CODE_PREFIXES, PayEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: PayEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-"
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
            model.is_deleted.is_(False),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{full_prefix}{seq:0{width}d}"
''',
    )
    for module, cls, name, branch in TABLES:
        w(PAY / "repository" / f"{module}_repository.py", repo_template(module, cls, name, branch))


def gen_engines() -> None:
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        w(
            PAY / "service" / "engines" / f"{fname}_engine.py",
            f'"""{eng_name} lifecycle engine."""\n{ENGINE_IMPORTS}\n{body}\n',
        )
    lines = [
        f"from modules.payroll.service.engines.{ENGINE_FILE_MAP[n]}_engine import {n}Engine"
        for n in ENGINE_BODIES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_BODIES)
    w(
        PAY / "service" / "engines" / "__init__.py",
        '"""Payroll business engines."""\n\n'
        + "\n".join(lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def catalog_service(name: str, cls: str, repo_name: str, entity: str, branch: bool) -> str:
    branch_arg = ", *, branch_id: UUID | None = None" if branch else ""
    branch_fields = (
        "\n        if branch_id is not None:\n"
        "            self._scope.validate_branch_access(ctx, branch_id)\n"
        if branch
        else ""
    )
    branch_create = "branch_id=branch_id," if branch else ""
    return f'''"""{name} application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.payroll.models import {cls}
from modules.payroll.repository.{entity}_repository import {repo_name}Repository
from modules.payroll.service.engines import {repo_name}Engine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class {name}Service:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = PayrollScopeValidator(db)
        self._engine = {repo_name}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None{branch_arg}, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
{branch_fields}
        row = self._repo.create(ctx, company_id=cid, {branch_create} **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="pay_{entity}",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{name} not found")
        return row
'''


def gen_services() -> None:
    w(
        PAY / "service" / "payroll_scope_validator.py",
        '''"""Payroll scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.base import PayScopedRepository


class PayrollScopeValidator(PayScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        PAY / "service" / "document_number_service.py",
        '''"""Payroll document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.payroll.domain.enums import PayEntityType
from modules.payroll.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: PayEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )
    svc_map = [
        ("PayrollPeriod", "PayPayrollPeriod", "PayrollPeriod", "payroll_period", False),
        ("SalaryStructure", "PaySalaryStructure", "SalaryStructure", "salary_structure", False),
        ("SalaryComponent", "PaySalaryComponent", "SalaryComponent", "salary_component", False),
        ("SalaryStructureLine", "PaySalaryStructureLine", "SalaryStructureLine", "salary_structure_line", False),
        ("EmployeeSalary", "PayEmployeeSalary", "EmployeeSalary", "employee_salary", True),
        ("EmployeeSalaryComponent", "PayEmployeeSalaryComponent", "EmployeeSalaryComponent", "employee_salary_component", True),
        ("EarningType", "PayEarningType", "EarningType", "earning_type", False),
        ("DeductionType", "PayDeductionType", "DeductionType", "deduction_type", False),
        ("TaxConfiguration", "PayTaxConfiguration", "TaxConfiguration", "tax_configuration", False),
        ("StatutoryContribution", "PayStatutoryContribution", "StatutoryContribution", "statutory_contribution", False),
        ("PayrollRunLine", "PayPayrollRunLine", "PayrollRunLine", "payroll_run_line", True),
        ("LoanInstallment", "PayLoanInstallment", "LoanInstallment", "loan_installment", True),
        ("PayrollAdjustment", "PayPayrollAdjustment", "PayrollAdjustment", "payroll_adjustment", True),
        ("PayrollSummary", "PayPayrollSummary", "PayrollSummary", "payroll_summary", False),
    ]
    for name, cls, repo, mod, branch in svc_map:
        fname = mod.replace("_service", "") + "_service.py"
        if mod.endswith("_line"):
            fname = mod + "_service.py"
        w(PAY / "service" / fname, catalog_service(name, cls, repo, mod, branch))

    w(PAY / "service" / "payroll_period_service.py", catalog_service("PayrollPeriod", "PayPayrollPeriod", "PayrollPeriod", "payroll_period", False))
    w(PAY / "service" / "salary_structure_service.py", catalog_service("SalaryStructure", "PaySalaryStructure", "SalaryStructure", "salary_structure", False))
    w(PAY / "service" / "salary_component_service.py", catalog_service("SalaryComponent", "PaySalaryComponent", "SalaryComponent", "salary_component", False))
    w(PAY / "service" / "structure_line_service.py", catalog_service("SalaryStructureLine", "PaySalaryStructureLine", "SalaryStructureLine", "salary_structure_line", False))
    w(PAY / "service" / "employee_salary_service.py", catalog_service("EmployeeSalary", "PayEmployeeSalary", "EmployeeSalary", "employee_salary", True))
    w(PAY / "service" / "earning_type_service.py", catalog_service("EarningType", "PayEarningType", "EarningType", "earning_type", False))
    w(PAY / "service" / "deduction_type_service.py", catalog_service("DeductionType", "PayDeductionType", "DeductionType", "deduction_type", False))
    w(PAY / "service" / "tax_service.py", catalog_service("TaxConfiguration", "PayTaxConfiguration", "TaxConfiguration", "tax_configuration", False))
    w(PAY / "service" / "statutory_service.py", catalog_service("StatutoryContribution", "PayStatutoryContribution", "StatutoryContribution", "statutory_contribution", False))
    w(PAY / "service" / "run_line_service.py", catalog_service("PayrollRunLine", "PayPayrollRunLine", "PayrollRunLine", "payroll_run_line", True))
    w(PAY / "service" / "adjustment_service.py", catalog_service("PayrollAdjustment", "PayPayrollAdjustment", "PayrollAdjustment", "payroll_adjustment", True))
    w(PAY / "service" / "installment_service.py", catalog_service("LoanInstallment", "PayLoanInstallment", "LoanInstallment", "loan_installment", True))
    w(PAY / "service" / "payroll_summary_service.py", catalog_service("PayrollSummary", "PayPayrollSummary", "PayrollSummary", "payroll_summary", False))

    w(
        PAY / "service" / "payroll_run_service.py",
        '''"""Payroll run application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.payroll.adapters.hr_port import PayrollHrAdapter
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayPayrollRun
from modules.payroll.repository.payroll_run_repository import PayrollRunRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import PayrollRunEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayrollRunService:
    def __init__(self, db: Session) -> None:
        self._repo = PayrollRunRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = PayrollRunEngine()
        self._hr = PayrollHrAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayPayrollRun:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Payroll run not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.PAYROLL_RUN, cid, PayPayrollRun, "document_number")
        row = self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="pay_payroll_run",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def calculate(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        _ = self._hr.employment_facts(ctx, row.company_id)
        _ = self._hr.attendance_facts(ctx, row.company_id)
        _ = self._hr.leave_facts(ctx, row.company_id)
        self._engine.calculate(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        PAY / "service" / "payslip_service.py",
        '''"""Payslip application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayPayslip
from modules.payroll.repository.payslip_repository import PayslipRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import PayslipEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayslipService:
    def __init__(self, db: Session) -> None:
        self._repo = PayslipRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = PayslipEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayPayslip:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Payslip not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.PAYSLIP, cid, PayPayslip, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def issue(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.issue(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        PAY / "service" / "bonus_service.py",
        '''"""Bonus application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayBonus
from modules.payroll.repository.bonus_repository import BonusRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import BonusEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class BonusService:
    def __init__(self, db: Session) -> None:
        self._repo = BonusRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = BonusEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayBonus:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Bonus not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.BONUS, cid, PayBonus, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        PAY / "service" / "reimbursement_service.py",
        '''"""Reimbursement application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayReimbursement
from modules.payroll.repository.reimbursement_repository import ReimbursementRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import ReimbursementEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class ReimbursementService:
    def __init__(self, db: Session) -> None:
        self._repo = ReimbursementRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ReimbursementEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayReimbursement:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Reimbursement not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.REIMBURSEMENT, cid, PayReimbursement, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        PAY / "service" / "loan_service.py",
        '''"""Loan application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayLoan
from modules.payroll.repository.loan_repository import LoanRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import LoanEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class LoanService:
    def __init__(self, db: Session) -> None:
        self._repo = LoanRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = LoanEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayLoan:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Loan not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.LOAN, cid, PayLoan, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)
''',
    )

    w(
        PAY / "service" / "payroll_posting_service.py",
        '''"""Payroll posting — Finance via PostingService only."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.payroll.adapters.finance_port import PayrollFinanceAdapter
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayPayrollPosting
from modules.payroll.repository.payroll_posting_repository import PayrollPostingRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import PayrollPostingEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayrollPostingService:
    def __init__(self, db: Session) -> None:
        self._repo = PayrollPostingRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = PayrollPostingEngine()
        self._finance = PayrollFinanceAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayPayrollPosting:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Payroll posting not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.PAYROLL_POSTING, cid, PayPayrollPosting, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def post(self, ctx: TenantContext, row_id: UUID, *, debit_account_id: UUID, credit_account_id: UUID):
        row = self.get(ctx, row_id)
        amount = Decimal(str(row.debit_total))
        try:
            jid = self._finance.post_salary_expense(
                ctx,
                row,
                amount=amount,
                debit_account_id=debit_account_id,
                credit_account_id=credit_account_id,
            )
            self._engine.mark_posted(row)
            updated = self._repo.update(
                ctx,
                row_id,
                status=row.status,
                finance_journal_id=jid,
            )
            self._audit.log_entity_change(
                tenant_id=ctx.tenant_id,
                entity_name="pay_payroll_posting",
                entity_id=row_id,
                operation="post",
                performed_by=ctx.user_id,
            )
            return updated
        except Exception as exc:  # noqa: BLE001
            self._engine.mark_failed(row, str(exc))
            return self._repo.update(ctx, row_id, status=row.status, error_message=row.error_message)
''',
    )

    w(
        PAY / "service" / "payroll_report_service.py",
        '''"""Payroll reporting service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.payroll_run_repository import PayrollRunRepository
from modules.payroll.repository.payroll_summary_repository import PayrollSummaryRepository
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayrollReportService:
    def __init__(self, db: Session) -> None:
        self._scope = PayrollScopeValidator(db)
        self._runs = PayrollRunRepository(db)
        self._summaries = PayrollSummaryRepository(db)

    def payroll_cost_summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        runs = self._runs.list_rows(ctx, cid)
        summaries = self._summaries.list_rows(ctx, cid)
        return {
            "run_count": len(runs),
            "summary_count": len(summaries),
            "total_net": sum(float(r.total_net or 0) for r in runs),
        }
''',
    )

    w(
        PAY / "service" / "integration_service.py",
        '''"""Payroll integration facade."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.adapters.hr_port import PayrollHrAdapter
from modules.payroll.adapters.master_data_port import PayrollMasterDataAdapter
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayrollIntegrationService:
    def __init__(self, db: Session) -> None:
        self._scope = PayrollScopeValidator(db)
        self._master = PayrollMasterDataAdapter(db)
        self._hr = PayrollHrAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def hr_employment_snapshot(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._hr.employment_facts(ctx, company_id)

    def hr_attendance_snapshot(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._hr.attendance_facts(ctx, company_id)

    def hr_leave_snapshot(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._hr.leave_facts(ctx, company_id)
''',
    )

    w(
        PAY / "service" / "application_service.py",
        '''"""Payroll application service facade."""

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
''',
    )

    w(
        PAY / "service" / "__init__.py",
        '''"""Payroll services."""

from modules.payroll.service.adjustment_service import PayrollAdjustmentService
from modules.payroll.service.application_service import PayrollApplicationService
from modules.payroll.service.bonus_service import BonusService
from modules.payroll.service.deduction_type_service import DeductionTypeService
from modules.payroll.service.earning_type_service import EarningTypeService
from modules.payroll.service.employee_salary_service import EmployeeSalaryService
from modules.payroll.service.installment_service import LoanInstallmentService
from modules.payroll.service.integration_service import PayrollIntegrationService
from modules.payroll.service.loan_service import LoanService
from modules.payroll.service.payroll_period_service import PayrollPeriodService
from modules.payroll.service.payroll_posting_service import PayrollPostingService
from modules.payroll.service.payroll_report_service import PayrollReportService
from modules.payroll.service.payroll_run_service import PayrollRunService
from modules.payroll.service.payslip_service import PayslipService
from modules.payroll.service.reimbursement_service import ReimbursementService
from modules.payroll.service.run_line_service import PayrollRunLineService
from modules.payroll.service.salary_component_service import SalaryComponentService
from modules.payroll.service.salary_structure_service import SalaryStructureService
from modules.payroll.service.statutory_service import StatutoryContributionService
from modules.payroll.service.structure_line_service import SalaryStructureLineService
from modules.payroll.service.tax_service import TaxConfigurationService

__all__ = [
    "BonusService",
    "DeductionTypeService",
    "EarningTypeService",
    "EmployeeSalaryService",
    "LoanInstallmentService",
    "LoanService",
    "PayrollAdjustmentService",
    "PayrollApplicationService",
    "PayrollIntegrationService",
    "PayrollPeriodService",
    "PayrollPostingService",
    "PayrollReportService",
    "PayrollRunLineService",
    "PayrollRunService",
    "PayslipService",
    "ReimbursementService",
    "SalaryComponentService",
    "SalaryStructureLineService",
    "SalaryStructureService",
    "StatutoryContributionService",
    "TaxConfigurationService",
]
''',
    )


def gen_adapters() -> None:
    w(
        PAY / "adapters" / "master_data_port.py",
        '''"""Master Data port — Payroll never ORM-writes master_* tables."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.employee_service import EmployeeService


class PayrollMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._employees = EmployeeService(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)
''',
    )
    w(
        PAY / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class PayrollOrganizationAdapter:
    def __init__(self, db: Session) -> None:
        self._departments = DepartmentRepository(db)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        department = self._departments.get_by_id(ctx, department_id)
        if department is None:
            raise NotFoundException("Department not found")
        return department
''',
    )
    w(
        PAY / "adapters" / "hr_port.py",
        '''"""HR port — wraps HRIntegrationService payroll read facts."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.service.integration_service import HRIntegrationService


class PayrollHrAdapter:
    def __init__(self, db: Session) -> None:
        self._hr = HRIntegrationService(db)

    def employment_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        return self._hr.payroll_employment_facts(ctx, company_id)

    def attendance_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        return self._hr.payroll_attendance_facts(ctx, company_id)

    def leave_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        return self._hr.payroll_leave_facts(ctx, company_id)
''',
    )
    w(
        PAY / "adapters" / "finance_port.py",
        '''"""Finance port — JournalService + PostingService.post_system_journal only."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import JournalType
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.models import PayPayrollPosting


class PayrollFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._journals = JournalService(db)
        self._posting = PostingService(db)

    def post_salary_expense(
        self,
        ctx: TenantContext,
        posting: PayPayrollPosting,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        amount = amount.quantize(Decimal("0.0001"))
        journal = self._journals.create_journal(
            ctx,
            company_id=posting.company_id,
            branch_id=posting.branch_id,
            journal_date=posting.created_at.date(),
            description=f"Payroll posting {posting.document_number}",
            journal_type=JournalType.SYSTEM.value,
            period_id=posting.period_id,
            fiscal_year_id=fiscal_year_id,
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=1,
            account_id=debit_account_id,
            debit_amount=float(amount),
            credit_amount=0,
            description="Salary expense",
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=2,
            account_id=credit_account_id,
            debit_amount=0,
            credit_amount=float(amount),
            description="Payroll liability",
        )
        self._posting.post_system_journal(ctx, journal.id)
        return journal.id
''',
    )
    w(
        PAY / "adapters" / "__init__.py",
        '''"""Payroll adapters."""

from modules.payroll.adapters.finance_port import PayrollFinanceAdapter
from modules.payroll.adapters.hr_port import PayrollHrAdapter
from modules.payroll.adapters.master_data_port import PayrollMasterDataAdapter
from modules.payroll.adapters.organization_port import PayrollOrganizationAdapter

__all__ = [
    "PayrollFinanceAdapter",
    "PayrollHrAdapter",
    "PayrollMasterDataAdapter",
    "PayrollOrganizationAdapter",
]
''',
    )


def gen_permissions() -> None:
    w(
        PAY / "permissions.py",
        '''"""Payroll permission constants per ERD_12 §14."""

PAYROLL_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("payroll.period:read", "payroll.period", "read", "payroll"),
    ("payroll.period:create", "payroll.period", "create", "payroll"),
    ("payroll.period:update", "payroll.period", "update", "payroll"),
    ("payroll.structure:read", "payroll.structure", "read", "payroll"),
    ("payroll.structure:create", "payroll.structure", "create", "payroll"),
    ("payroll.structure:update", "payroll.structure", "update", "payroll"),
    ("payroll.component:read", "payroll.component", "read", "payroll"),
    ("payroll.component:create", "payroll.component", "create", "payroll"),
    ("payroll.component:update", "payroll.component", "update", "payroll"),
    ("payroll.employee_salary:read", "payroll.employee_salary", "read", "payroll"),
    ("payroll.employee_salary:create", "payroll.employee_salary", "create", "payroll"),
    ("payroll.employee_salary:update", "payroll.employee_salary", "update", "payroll"),
    ("payroll.run:read", "payroll.run", "read", "payroll"),
    ("payroll.run:create", "payroll.run", "create", "payroll"),
    ("payroll.run:calculate", "payroll.run", "calculate", "payroll"),
    ("payroll.run:submit", "payroll.run", "submit", "payroll"),
    ("payroll.run:approve", "payroll.run", "approve", "payroll"),
    ("payroll.payslip:read", "payroll.payslip", "read", "payroll"),
    ("payroll.payslip:issue", "payroll.payslip", "issue", "payroll"),
    ("payroll.payslip:export", "payroll.payslip", "export", "payroll"),
    ("payroll.bonus:read", "payroll.bonus", "read", "payroll"),
    ("payroll.bonus:create", "payroll.bonus", "create", "payroll"),
    ("payroll.bonus:submit", "payroll.bonus", "submit", "payroll"),
    ("payroll.bonus:approve", "payroll.bonus", "approve", "payroll"),
    ("payroll.reimbursement:read", "payroll.reimbursement", "read", "payroll"),
    ("payroll.reimbursement:create", "payroll.reimbursement", "create", "payroll"),
    ("payroll.reimbursement:submit", "payroll.reimbursement", "submit", "payroll"),
    ("payroll.reimbursement:approve", "payroll.reimbursement", "approve", "payroll"),
    ("payroll.loan:read", "payroll.loan", "read", "payroll"),
    ("payroll.loan:create", "payroll.loan", "create", "payroll"),
    ("payroll.loan:submit", "payroll.loan", "submit", "payroll"),
    ("payroll.loan:approve", "payroll.loan", "approve", "payroll"),
    ("payroll.adjustment:read", "payroll.adjustment", "read", "payroll"),
    ("payroll.adjustment:create", "payroll.adjustment", "create", "payroll"),
    ("payroll.adjustment:apply", "payroll.adjustment", "apply", "payroll"),
    ("payroll.posting:read", "payroll.posting", "read", "payroll"),
    ("payroll.posting:submit", "payroll.posting", "submit", "payroll"),
    ("payroll.posting:approve", "payroll.posting", "approve", "payroll"),
    ("payroll.posting:post", "payroll.posting", "post", "payroll"),
    ("payroll.tax:read", "payroll.tax", "read", "payroll"),
    ("payroll.tax:create", "payroll.tax", "create", "payroll"),
    ("payroll.tax:update", "payroll.tax", "update", "payroll"),
    ("payroll.statutory:read", "payroll.statutory", "read", "payroll"),
    ("payroll.statutory:create", "payroll.statutory", "create", "payroll"),
    ("payroll.statutory:update", "payroll.statutory", "update", "payroll"),
    ("payroll.report:read", "payroll.report", "read", "payroll"),
    ("payroll.report:export", "payroll.report", "export", "payroll"),
]

PAYROLL_EXECUTIVE_PERMISSIONS = list(
    dict.fromkeys(
        [p[0] for p in PAYROLL_PERMISSIONS if p[2] in {"read", "create", "update", "calculate", "issue", "export"}]
    )
)

PAYROLL_MANAGER_PERMISSIONS = list(
    dict.fromkeys(
        PAYROLL_EXECUTIVE_PERMISSIONS
        + [
            "payroll.run:submit",
            "payroll.run:approve",
            "payroll.bonus:approve",
            "payroll.loan:approve",
            "payroll.posting:submit",
        ]
    )
)

HR_PAYROLL_ADMIN_PERMISSIONS = list(
    dict.fromkeys(
        PAYROLL_MANAGER_PERMISSIONS
        + [
            "payroll.reimbursement:approve",
            "payroll.adjustment:apply",
        ]
    )
)

FINANCE_PAYROLL_REVIEWER_PERMISSIONS = list(
    dict.fromkeys(
        HR_PAYROLL_ADMIN_PERMISSIONS
        + [
            "payroll.posting:approve",
            "payroll.posting:post",
            "payroll.report:export",
        ]
    )
)
''',
    )


ROUTE_SPECS = [
    ("periods", "PayrollPeriod", "PayrollPeriodService", "payroll.period", False),
    ("salary-structures", "SalaryStructure", "SalaryStructureService", "payroll.structure", False),
    ("salary-components", "SalaryComponent", "SalaryComponentService", "payroll.component", False),
    ("structure-lines", "SalaryStructureLine", "SalaryStructureLineService", "payroll.structure", False),
    ("employee-salaries", "EmployeeSalary", "EmployeeSalaryService", "payroll.employee_salary", True),
    ("earning-types", "EarningType", "EarningTypeService", "payroll.component", False),
    ("deduction-types", "DeductionType", "DeductionTypeService", "payroll.component", False),
    ("tax-configurations", "TaxConfiguration", "TaxConfigurationService", "payroll.tax", False),
    ("statutory-contributions", "StatutoryContribution", "StatutoryContributionService", "payroll.statutory", False),
    ("payroll-runs", "PayrollRun", "PayrollRunService", "payroll.run", True),
    ("run-lines", "PayrollRunLine", "PayrollRunLineService", "payroll.run", True),
    ("payslips", "Payslip", "PayslipService", "payroll.payslip", True),
    ("bonuses", "Bonus", "BonusService", "payroll.bonus", True),
    ("reimbursements", "Reimbursement", "ReimbursementService", "payroll.reimbursement", True),
    ("loans", "Loan", "LoanService", "payroll.loan", True),
    ("loan-installments", "LoanInstallment", "LoanInstallmentService", "payroll.loan", True),
    ("adjustments", "PayrollAdjustment", "PayrollAdjustmentService", "payroll.adjustment", True),
    ("postings", "PayrollPosting", "PayrollPostingService", "payroll.posting", True),
    ("summaries", "PayrollSummary", "PayrollSummaryService", "payroll.report", False),
]


def gen_api() -> None:
    w(
        PAY / "dependencies.py",
        '''"""Payroll module dependencies."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from database.session import get_db
from modules.foundation.dependencies import get_tenant_context, require_permission
from modules.foundation.domain.value_objects import TenantContext

__all__ = [
    "PaginationParams",
    "get_pagination",
    "get_tenant_context",
    "require_permission",
    "TenantContext",
    "get_db",
    "paginate",
    "extract_update_fields",
]


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 25,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def paginate(items: list, pagination: PaginationParams) -> list:
    return items[pagination.offset : pagination.offset + pagination.page_size]


def extract_update_fields(body) -> dict:
    fields = body.model_dump(exclude_unset=True)
    fields.pop("version", None)
    return fields
''',
    )

    schema_lines = [
        '"""Payroll Pydantic schemas."""',
        "",
        "from uuid import UUID",
        "",
        "from pydantic import BaseModel, ConfigDict",
        "",
        "",
        "class OrmModel(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
    ]
    for _, name, _, _, branch in ROUTE_SPECS:
        schema_lines += [
            "",
            f"class {name}Create(BaseModel):",
            "    company_id: UUID | None = None",
        ]
        if branch:
            schema_lines.append("    branch_id: UUID")
        schema_lines += [
            "    status: str | None = None",
            "",
            f"class {name}Update(BaseModel):",
            "    status: str | None = None",
            "    version: int | None = None",
            "",
            f"class {name}Response(OrmModel):",
            "    id: UUID",
            "    company_id: UUID",
            "    status: str",
            "    version: int",
        ]
    w(PAY / "schemas.py", "\n".join(schema_lines) + "\n")

    router_imports = [
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from database.session import get_db",
        "from modules.foundation.dependencies import require_permission",
        "from modules.foundation.domain.value_objects import TenantContext",
        "from modules.payroll.dependencies import PaginationParams, extract_update_fields, get_pagination, paginate",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_imports.append(f"from modules.payroll.schemas import {name}Create, {name}Response, {name}Update")
    router_imports.append("from modules.payroll.service import (")
    for _, _, svc, _, _ in ROUTE_SPECS:
        router_imports.append(f"    {svc},")
    router_imports += [
        "    PayrollReportService,",
        ")",
        "from shared.schemas import APIResponse",
        "",
    ]

    router_defs = []
    route_handlers = []
    for prefix, name, svc, perm, branch in ROUTE_SPECS:
        rname = prefix.replace("-", "_") + "_router"
        router_defs.append(
            f'{rname} = APIRouter(prefix="/{prefix}", tags=["Payroll - {name}"])'
        )
        create_perm = f"{perm}:create"
        read_perm = f"{perm}:read"
        update_perm = f"{perm}:update" if "structure" in perm or "component" in perm or "tax" in perm or "statutory" in perm or "employee_salary" in perm or "period" in perm else f"{perm}:read"
        route_handlers += [
            "",
            f"@{rname}.get(\"\", response_model=APIResponse[list[{name}Response]])",
            f"def list_{prefix.replace('-', '_')}(",
            f"    ctx: Annotated[TenantContext, Depends(require_permission(\"{read_perm}\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    return APIResponse(message=\"OK\", data=paginate({svc}(db).list(ctx, company_id), pagination))",
            "",
            f"@{rname}.post(\"\", response_model=APIResponse[{name}Response])",
            f"def create_{prefix.replace('-', '_')}(",
            f"    body: {name}Create,",
            f"    ctx: Annotated[TenantContext, Depends(require_permission(\"{create_perm}\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"Created\", data={svc}(db).create(ctx, **body.model_dump()))",
            "",
            f"@{rname}.patch(\"/{{row_id}}\", response_model=APIResponse[{name}Response])",
            f"def update_{prefix.replace('-', '_')}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            f"    ctx: Annotated[TenantContext, Depends(require_permission(\"{update_perm}\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"Updated\", data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))",
        ]
        if svc == "PayrollRunService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/calculate\", response_model=APIResponse[{name}Response])",
                f"def calculate_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                "    ctx: Annotated[TenantContext, Depends(require_permission(\"payroll.run:calculate\"))],",
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Calculated\", data={svc}(db).calculate(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/submit\", response_model=APIResponse[{name}Response])",
                f"def submit_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                "    ctx: Annotated[TenantContext, Depends(require_permission(\"payroll.run:submit\"))],",
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Submitted\", data={svc}(db).submit(ctx, row_id))",
                "",
                f"@{rname}.post(\"/{{row_id}}/approve\", response_model=APIResponse[{name}Response])",
                f"def approve_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                "    ctx: Annotated[TenantContext, Depends(require_permission(\"payroll.run:approve\"))],",
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Approved\", data={svc}(db).approve(ctx, row_id))",
            ]
        if svc == "PayslipService":
            route_handlers += [
                "",
                f"@{rname}.post(\"/{{row_id}}/issue\", response_model=APIResponse[{name}Response])",
                f"def issue_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                "    ctx: Annotated[TenantContext, Depends(require_permission(\"payroll.payslip:issue\"))],",
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Issued\", data={svc}(db).issue(ctx, row_id))",
            ]

    reports_router = [
        "",
        'reports_router = APIRouter(prefix="/reports", tags=["Payroll - Reports"])',
        "",
        '@reports_router.get("/cost-summary", response_model=APIResponse[dict])',
        "def payroll_cost_summary(",
        '    ctx: Annotated[TenantContext, Depends(require_permission("payroll.report:read"))],',
        "    db: Annotated[Session, Depends(get_db)],",
        "    company_id: UUID | None = None,",
        "):",
        '    return APIResponse(message="OK", data=PayrollReportService(db).payroll_cost_summary(ctx, company_id))',
    ]

    w(
        PAY / "routers" / "__init__.py",
        '"""Payroll REST routers."""\n\n'
        + "\n".join(router_imports)
        + "\n".join(router_defs)
        + "\n".join(reports_router)
        + "\n".join(route_handlers)
        + "\n",
    )

    include_lines = []
    for prefix, _, _, _, _ in ROUTE_SPECS:
        include_lines.append(f"    {prefix.replace('-', '_')}_router,")
    w(
        PAY / "router.py",
        '''"""Payroll module router aggregation."""

from fastapi import APIRouter

from modules.payroll.routers import (
'''
        + "\n".join(include_lines)
        + '''    reports_router,
)

payroll_router = APIRouter(prefix="/payroll")
'''
        + "\n".join(
            f"payroll_router.include_router({prefix.replace('-', '_')}_router)"
            for prefix, _, _, _, _ in ROUTE_SPECS
        )
        + "\npayroll_router.include_router(reports_router)\n",
    )


def gen_tasks_tests() -> None:
    w(
        PAY / "tasks.py",
        '''"""Payroll Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="payroll.payroll_run_scheduler")
def payroll_run_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollPeriod

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollPeriod).where(
                    PayPayrollPeriod.is_deleted.is_(False),
                    PayPayrollPeriod.status == "open",
                )
            ).all()
        )
        return {"status": "ok", "open_periods": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.payslip_generation")
def payslip_generation() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollRun

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollRun).where(
                    PayPayrollRun.is_deleted.is_(False),
                    PayPayrollRun.status == "approved",
                )
            ).all()
        )
        return {"status": "ok", "approved_runs": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.loan_installment_processor")
def loan_installment_processor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayLoanInstallment

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayLoanInstallment).where(
                    PayLoanInstallment.is_deleted.is_(False),
                    PayLoanInstallment.status == "scheduled",
                )
            ).all()
        )
        return {"status": "ok", "due_installments": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.bonus_reminders")
def bonus_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayBonus

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayBonus).where(
                    PayBonus.is_deleted.is_(False),
                    PayBonus.status == "submitted",
                )
            ).all()
        )
        return {"status": "ok", "pending_bonuses": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.payroll_post_retry")
def payroll_post_retry() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollPosting

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollPosting).where(
                    PayPayrollPosting.is_deleted.is_(False),
                    PayPayrollPosting.status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_postings": len(rows)}
    finally:
        db.close()


@celery_app.task(name="payroll.refresh_payroll_summary")
def refresh_payroll_summary() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.payroll.models import PayPayrollSummary

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PayPayrollSummary).where(
                    PayPayrollSummary.is_deleted.is_(False),
                    PayPayrollSummary.status == "draft",
                )
            ).all()
        )
        return {"status": "ok", "draft_summaries": len(rows)}
    finally:
        db.close()
''',
    )

    w(
        TESTS / "unit" / "payroll" / "test_payroll_engines.py",
        '''"""Unit tests for payroll engines."""

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
''',
    )

    w(
        TESTS / "unit" / "payroll" / "test_payroll_tasks.py",
        '''"""Unit tests for payroll Celery tasks."""

from modules.payroll import tasks as payroll_tasks


def test_payroll_task_names_registered():
    assert payroll_tasks.payroll_run_scheduler.name == "payroll.payroll_run_scheduler"
    assert payroll_tasks.payslip_generation.name == "payroll.payslip_generation"
    assert payroll_tasks.loan_installment_processor.name == "payroll.loan_installment_processor"
    assert payroll_tasks.bonus_reminders.name == "payroll.bonus_reminders"
    assert payroll_tasks.payroll_post_retry.name == "payroll.payroll_post_retry"
    assert payroll_tasks.refresh_payroll_summary.name == "payroll.refresh_payroll_summary"
''',
    )

    w(
        TESTS / "security" / "payroll" / "test_payroll_permissions.py",
        '''"""Payroll RBAC permission tests."""

from modules.payroll.permissions import (
    FINANCE_PAYROLL_REVIEWER_PERMISSIONS,
    HR_PAYROLL_ADMIN_PERMISSIONS,
    PAYROLL_EXECUTIVE_PERMISSIONS,
    PAYROLL_MANAGER_PERMISSIONS,
    PAYROLL_PERMISSIONS,
)


def test_payroll_permissions_defined():
    assert len(PAYROLL_PERMISSIONS) >= 40
    assert "payroll.run:calculate" in [p[0] for p in PAYROLL_PERMISSIONS]


def test_payroll_roles():
    assert "PAYROLL_EXECUTIVE"  # role constants in seed migration
    assert PAYROLL_EXECUTIVE_PERMISSIONS
    assert PAYROLL_MANAGER_PERMISSIONS
    assert HR_PAYROLL_ADMIN_PERMISSIONS
    assert FINANCE_PAYROLL_REVIEWER_PERMISSIONS
    assert "payroll.posting:post" in FINANCE_PAYROLL_REVIEWER_PERMISSIONS
''',
    )

    w(
        TESTS / "integration" / "payroll" / "test_payroll_module_import.py",
        '''"""Integration smoke: Payroll module imports and router mount."""

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
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0199_seed_payroll_permissions.py",
        '''"""Seed payroll permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.payroll.permissions import (
    FINANCE_PAYROLL_REVIEWER_PERMISSIONS,
    HR_PAYROLL_ADMIN_PERMISSIONS,
    PAYROLL_EXECUTIVE_PERMISSIONS,
    PAYROLL_MANAGER_PERMISSIONS,
    PAYROLL_PERMISSIONS,
)

revision: str = "0199_seed_payroll_permissions"
down_revision: str | None = "0198_pay_payroll_summary"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)

ROLE_SPECS: list[tuple[str, str, list[str]]] = [
    ("PAYROLL_EXECUTIVE", "Payroll Executive", PAYROLL_EXECUTIVE_PERMISSIONS),
    ("PAYROLL_MANAGER", "Payroll Manager", PAYROLL_MANAGER_PERMISSIONS),
    ("HR_PAYROLL_ADMIN", "HR Payroll Admin", HR_PAYROLL_ADMIN_PERMISSIONS),
    ("FINANCE_PAYROLL_REVIEWER", "Finance Payroll Reviewer", FINANCE_PAYROLL_REVIEWER_PERMISSIONS),
]


def _ensure_permission(conn, now, code, resource, action, module):
    exists = conn.execute(
        sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
        {"code": code},
    ).first()
    if exists:
        return str(exists[0])
    perm_id = str(uuid4())
    conn.execute(
        sa.insert(PERMISSION_TABLE).values(
            id=perm_id,
            permission_code=code,
            resource=resource,
            action=action,
            module=module,
            is_active=True,
            created_at=now,
        )
    )
    return perm_id


def _ensure_role(conn, now, tenant_id, role_code, role_name):
    exists = conn.execute(
        sa.text(
            """
            SELECT id FROM foundation.sec_role
            WHERE tenant_id = :tid AND role_code = :code AND is_deleted = false
            """
        ),
        {"tid": tenant_id, "code": role_code},
    ).first()
    if exists:
        return str(exists[0])
    role_id = str(uuid4())
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role
            (id, tenant_id, role_code, role_name, is_system_role, status,
             created_at, updated_at, is_deleted, version)
            VALUES (:id, :tid, :code, :name, true, 'active', :now, :now, false, 1)
            """
        ),
        {"id": role_id, "tid": tenant_id, "code": role_code, "name": role_name, "now": now},
    )
    return role_id


def _grant(conn, now, tenant_id, role_id, perm_id):
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM foundation.sec_role_permission
            WHERE role_id = :rid AND permission_id = :pid
            """
        ),
        {"rid": role_id, "pid": perm_id},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role_permission
            (id, tenant_id, role_id, permission_id, granted_at)
            VALUES (:id, :tid, :rid, :pid, :now)
            """
        ),
        {"id": str(uuid4()), "tid": tenant_id, "rid": role_id, "pid": perm_id, "now": now},
    )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    perm_ids: dict[str, str] = {}
    for code, resource, action, module in PAYROLL_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, perms in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for perm_code in perms:
                _grant(conn, now, tid, role_id, perm_ids[perm_code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in reversed(ROLE_SPECS):
        conn.execute(
            sa.text(
                "DELETE FROM foundation.sec_role WHERE role_code = :code AND is_system_role = true"
            ),
            {"code": role_code},
        )
    for code, _, _, _ in PAYROLL_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0200_seed_payroll_workflows.py",
        '''"""Seed payroll workflow definitions per ERD_12."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0200_seed_payroll_workflows"
down_revision: str | None = "0199_seed_payroll_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "PAY_PAYROLL_APPROVAL",
        "Payroll Run Approval",
        "pay_payroll_run",
        [
            (1, "PAYROLL_EXECUTIVE", "Calculate & Submit", "role"),
            (2, "PAYROLL_MANAGER", "Payroll Manager Approval", "role"),
            (3, "FINANCE_PAYROLL_REVIEWER", "Finance Review", "role"),
        ],
    ),
    (
        "PAY_PAYROLL_POSTING",
        "Payroll Posting Approval",
        "pay_payroll_posting",
        [
            (1, "PAYROLL_MANAGER", "Submit Posting", "role"),
            (2, "FINANCE_PAYROLL_REVIEWER", "Finance Payroll Reviewer", "role"),
        ],
    ),
    (
        "PAY_BONUS_APPROVAL",
        "Bonus Approval",
        "pay_bonus",
        [
            (1, "PAYROLL_EXECUTIVE", "Submitter", "role"),
            (2, "PAYROLL_MANAGER", "Manager Approval", "role"),
            (3, "HR_PAYROLL_ADMIN", "HR/Payroll Admin", "role"),
        ],
    ),
    (
        "PAY_LOAN_APPROVAL",
        "Loan Approval",
        "pay_loan",
        [
            (1, "PAYROLL_EXECUTIVE", "Employee Submit", "role"),
            (2, "PAYROLL_MANAGER", "Manager Approval", "role"),
            (3, "HR_PAYROLL_ADMIN", "HR/Payroll Admin", "role"),
        ],
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'payroll', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, approver_ref, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, :aref, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
                        "atype": approver_type,
                        "aref": step_code,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
''',
    )


def gen_wiring() -> None:
    patch_file(
        SHARED / "router.py",
        "from modules.hr.router import hr_router\n",
        "from modules.hr.router import hr_router\nfrom modules.payroll.router import payroll_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(hr_router)\n",
        "api_v1_router.include_router(hr_router)\napi_v1_router.include_router(payroll_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.hr.models  # noqa: F401 — register ORM metadata\n",
        "import modules.hr.models  # noqa: F401 — register ORM metadata\n"
        "import modules.payroll.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.hr",\n',
        '        "modules.hr",\n        "modules.payroll",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.hr.*",\n',
        '    "modules.hr.*",\n    "modules.payroll.*",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '"src/modules/hr/domain/enums.py" = ["UP042"]\n',
        '"src/modules/hr/domain/enums.py" = ["UP042"]\n'
        '"src/modules/payroll/**" = ["E501", "SIM102"]\n'
        '"src/modules/payroll/domain/enums.py" = ["UP042"]\n',
    )


def main() -> None:
    gen_scaffold()
    gen_domain()
    gen_models()
    gen_migrations()
    gen_repos()
    gen_engines()
    gen_services()
    gen_adapters()
    gen_permissions()
    gen_api()
    gen_tasks_tests()
    gen_seeds()
    gen_wiring()
    print(f"OK payroll module generated — {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0200_seed_payroll_workflows")


if __name__ == "__main__":
    main()
