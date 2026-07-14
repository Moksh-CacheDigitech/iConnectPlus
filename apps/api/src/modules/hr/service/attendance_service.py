"""Attendance service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import AttendanceRecordStatus
from modules.hr.repository.attendance_repository import AttendanceRepository
from modules.hr.service.engines import AttendanceEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class AttendanceService:
    def __init__(self, db: Session) -> None:
        self._repo = AttendanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = AttendanceEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Attendance not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            status=fields.pop("status", AttendanceRecordStatus.RECORDED.value),
            **fields,
        )

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        row = self.get(ctx, row_id)
        self._engine.adjust(row)
        return self._repo.update(ctx, row_id, status=AttendanceRecordStatus.ADJUSTED.value, **fields)

    def lock(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.lock(row)
        updated = self._repo.update(ctx, row_id, status=row.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_attendance",
            entity_id=row_id,
            operation="lock",
            performed_by=ctx.user_id,
        )
        return updated
