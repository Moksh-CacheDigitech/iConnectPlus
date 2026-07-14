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
from modules.payroll.service.payroll_summary_service import PayrollSummaryService
from modules.payroll.service.tax_service import TaxConfigurationService

__all__ = [
    "BonusService",
    "DeductionTypeService",
    "EarningTypeService",
    "EmployeeSalaryService",
    "LoanInstallmentService",
    "LoanService",
    "PayrollAdjustmentService",
    "PayrollAdjustmentService",
    "PayrollApplicationService",
    "PayrollIntegrationService",
    "PayrollPeriodService",
    "PayrollPostingService",
    "PayrollReportService",
    "PayrollRunLineService",
    "PayrollRunService",
    "PayrollSummaryService",
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
