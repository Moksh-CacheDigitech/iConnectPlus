"""Procurement vendor performance repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.models.performance import ProcVendorPerformance
from modules.procurement.repository.base import ProcScopedRepository


class PerformanceRepository(ProcScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_performance(
        self,
        ctx: TenantContext,
        company_id: UUID,
        *,
        vendor_id: UUID | None = None,
    ) -> list[ProcVendorPerformance]:
        stmt = select(ProcVendorPerformance).where(
            ProcVendorPerformance.company_id == company_id,
            ProcVendorPerformance.is_deleted.is_(False),
        )
        stmt = self.apply_proc_filter(stmt, ProcVendorPerformance, ctx)
        if vendor_id is not None:
            stmt = stmt.where(ProcVendorPerformance.vendor_id == vendor_id)
        return list(
            self.db.scalars(
                stmt.order_by(ProcVendorPerformance.calculated_at.desc())
            ).all()
        )
