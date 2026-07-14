"""Work center and machine services."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models.machine import MfgMachine
from modules.manufacturing.models.work_center import MfgWorkCenter
from modules.manufacturing.repository.machine_repository import MachineRepository
from modules.manufacturing.repository.work_center_repository import WorkCenterRepository
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator


class WorkCenterService:
    def __init__(self, db: Session) -> None:
        self._repo = WorkCenterRepository(db)
        self._scope = MfgScopeValidator(db)

    def list_work_centers(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_work_centers(ctx, cid)

    def get_work_center(self, ctx: TenantContext, work_center_id: UUID) -> MfgWorkCenter:
        row = self._repo.get(ctx, work_center_id)
        if row is None:
            raise NotFoundException("Work center not found")
        return row

    def create_work_center(self, ctx: TenantContext, **fields) -> MfgWorkCenter:
        company_id = fields["company_id"]
        self._scope.validate_company_access(ctx, company_id)
        return self._repo.create(ctx, **fields)

    def update_work_center(self, ctx: TenantContext, work_center_id: UUID, **fields) -> MfgWorkCenter:
        self.get_work_center(ctx, work_center_id)
        row = self._repo.update(ctx, work_center_id, **fields)
        assert row is not None
        return row


class MachineService:
    def __init__(self, db: Session) -> None:
        self._repo = MachineRepository(db)
        self._scope = MfgScopeValidator(db)

    def list_machines(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_machines(ctx, cid)

    def get_machine(self, ctx: TenantContext, machine_id: UUID) -> MfgMachine:
        row = self._repo.get(ctx, machine_id)
        if row is None:
            raise NotFoundException("Machine not found")
        return row

    def create_machine(self, ctx: TenantContext, **fields) -> MfgMachine:
        self._scope.validate_company_access(ctx, fields["company_id"])
        return self._repo.create(ctx, **fields)

    def update_machine(self, ctx: TenantContext, machine_id: UUID, **fields) -> MfgMachine:
        self.get_machine(ctx, machine_id)
        if "status" in fields and fields["status"] is not None:
            fields["last_status_at"] = datetime.now(timezone.utc)
        row = self._repo.update(ctx, machine_id, **fields)
        assert row is not None
        return row
