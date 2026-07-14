"""Assemble and complete _gen_payroll_module.py — run once then delete."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "_gen_payroll_module.py"
TAIL = ROOT / "scripts" / "_gen_payroll_module.tail"

head = SCRIPT.read_text(encoding="utf-8")

remainder = r'''

MODELS["tax_configuration"] = r\'\'\'"""Tax configuration ORM."""

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
\'\'\'

MODELS["statutory_contribution"] = r\'\'\'"""Statutory contribution rate ORM."""

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
\'\'\'

MODELS["payroll_run"] = r\'\'\'"""Payroll run header ORM."""

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
\'\'\'

MODELS["payroll_run_line"] = r\'\'\'"""Payroll run line ORM."""

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
\'\'\'

MODELS["payslip"] = r\'\'\'"""Payslip ORM."""

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
\'\'\'

MODELS["bonus"] = r\'\'\'"""Bonus ORM."""

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
\'\'\'

MODELS["reimbursement"] = r\'\'\'"""Reimbursement ORM."""

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
\'\'\'

MODELS["loan"] = r\'\'\'"""Loan ORM."""

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
\'\'\'

MODELS["loan_installment"] = r\'\'\'"""Loan installment schedule ORM."""

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
\'\'\'

MODELS["payroll_adjustment"] = r\'\'\'"""Payroll adjustment ORM."""

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
\'\'\'

MODELS["payroll_posting"] = r\'\'\'"""Payroll posting integration ORM."""

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
\'\'\'

MODELS["payroll_summary"] = r\'\'\'"""Payroll summary aggregate ORM."""

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
\'\'\'

'''

# Import generation functions from companion module
from _payroll_gen_functions import append_functions  # type: ignore

full = head + TAIL.read_text(encoding="utf-8") + remainder
full = append_functions(full)
SCRIPT.write_text(full, encoding="utf-8")
print(f"assembled {SCRIPT} ({len(full.splitlines())} lines)")
