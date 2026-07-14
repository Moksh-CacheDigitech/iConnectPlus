"""Payroll run application service."""

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
