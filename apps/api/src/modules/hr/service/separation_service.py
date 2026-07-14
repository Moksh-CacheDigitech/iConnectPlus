"""Separation service — completes via Master Data identity sync."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType
from modules.hr.models import HrSeparation
from modules.hr.repository.separation_repository import SeparationRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import SeparationEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class SeparationService:
    def __init__(self, db: Session) -> None:
        self._repo = SeparationRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = SeparationEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Separation not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        doc = self._numbers.generate(HrEntityType.SEPARATION, cid, HrSeparation, "document_number")
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            **fields,
        )

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID, *, stage: str = "manager"):
        row = self.get(ctx, row_id)
        if stage == "manager":
            self._engine.manager_approve(row)
        else:
            self._engine.hr_approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def complete(self, ctx: TenantContext, row_id: UUID, *, approved_last_working_date: date | None = None):
        row = self.get(ctx, row_id)
        self._engine.complete(row)
        lwd = approved_last_working_date or row.approved_last_working_date or row.requested_last_working_date
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            approved_last_working_date=lwd,
        )
        self._master.complete_separation_identity(
            ctx,
            row.employee_id,
            separation_type=row.separation_type,
            date_of_leaving=lwd,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_separation",
            entity_id=row_id,
            operation="complete",
            performed_by=ctx.user_id,
        )
        return updated
