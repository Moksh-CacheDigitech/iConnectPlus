"""Training services."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType
from modules.hr.models import HrTraining
from modules.hr.repository.training_attendance_repository import TrainingAttendanceRepository
from modules.hr.repository.training_repository import TrainingRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import TrainingAttendanceEngine, TrainingEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class TrainingService:
    def __init__(self, db: Session) -> None:
        self._repo = TrainingRepository(db)
        self._attendance = TrainingAttendanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = TrainingEngine()
        self._master = HrMasterDataAdapter(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Training not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        code = fields.pop("training_code", None) or self._numbers.generate(
            HrEntityType.TRAINING, cid, HrTraining, "training_code"
        )
        return self._repo.create(ctx, company_id=cid, training_code=code, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Training not found")
        return row

    def assign(
        self,
        ctx: TenantContext,
        training_id: UUID,
        *,
        branch_id: UUID,
        employee_id: UUID,
        company_id: UUID | None = None,
        **fields,
    ):
        training = self.get(ctx, training_id)
        cid = self._scope.resolve_company_id(ctx, company_id or training.company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        return self._attendance.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            training_id=training_id,
            employee_id=employee_id,
            **fields,
        )


class TrainingAttendanceService:
    def __init__(self, db: Session) -> None:
        self._repo = TrainingAttendanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = TrainingAttendanceEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def mark_attended(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Training attendance not found")
        self._engine.mark_attended(row)
        return self._repo.update(ctx, row_id, attendance_status=row.attendance_status)
