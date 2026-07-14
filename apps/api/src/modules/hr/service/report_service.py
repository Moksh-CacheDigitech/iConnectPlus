"""HR report service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.repository.attendance_repository import AttendanceRepository
from modules.hr.repository.leave_request_repository import LeaveRequestRepository
from modules.hr.repository.separation_repository import SeparationRepository
from modules.hr.service.hr_scope_validator import HrScopeValidator


class HRReportService:
    def __init__(self, db: Session) -> None:
        self._scope = HrScopeValidator(db)
        self._attendance = AttendanceRepository(db)
        self._leave = LeaveRequestRepository(db)
        self._separation = SeparationRepository(db)

    def summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        attendance = self._attendance.list_rows(ctx, cid)
        leaves = self._leave.list_rows(ctx, cid)
        separations = self._separation.list_rows(ctx, cid)
        return {
            "company_id": cid,
            "attendance_count": len(attendance),
            "leave_request_count": len(leaves),
            "approved_leave_count": sum(1 for r in leaves if r.status == "approved"),
            "separation_count": len(separations),
            "completed_separation_count": sum(1 for r in separations if r.status == "completed"),
        }
