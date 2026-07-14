"""Employment application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import EmploymentStatus, HrEntityType
from modules.hr.models import HrEmployment
from modules.hr.repository.employment_repository import EmploymentRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import EmploymentEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class EmploymentService:
    def __init__(self, db: Session) -> None:
        self._repo = EmploymentRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = EmploymentEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> HrEmployment:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Employment not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        status = fields.get("status", EmploymentStatus.DRAFT.value)
        if status in EmploymentEngine.ACTIVE_SET:
            self._ensure_single_active(ctx, cid, employee_id)
        doc = self._numbers.generate(HrEntityType.EMPLOYMENT, cid, HrEmployment, "document_number")
        row = self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            **fields,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_employment",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Employment not found")
        return row

    def activate(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._ensure_single_active(ctx, row.company_id, row.employee_id, exclude_id=row_id)
        self._engine.apply_activate(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def confirm(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.apply_confirm(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def end(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.apply_end(row)
        updated = self._repo.update(ctx, row_id, status=row.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_employment",
            entity_id=row_id,
            operation="end",
            performed_by=ctx.user_id,
        )
        return updated

    def _ensure_single_active(
        self,
        ctx: TenantContext,
        company_id: UUID,
        employee_id: UUID,
        exclude_id: UUID | None = None,
    ) -> None:
        for existing in self._repo.list_rows(ctx, company_id):
            if existing.employee_id != employee_id:
                continue
            if exclude_id and existing.id == exclude_id:
                continue
            if existing.status in EmploymentEngine.ACTIVE_SET:
                raise ConflictException("Employee already has an active employment record")
