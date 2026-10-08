"""Procurement sheet tracker repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.models.sheet_tracker import ProcSheetTracker
from modules.procurement.repository.base import ProcScopedRepository, utcnow


class SheetTrackerRepository(ProcScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_rows(self, ctx: TenantContext, company_id: UUID | None) -> list[ProcSheetTracker]:
        stmt = select(ProcSheetTracker).where(ProcSheetTracker.is_deleted.is_(False))
        stmt = self.apply_optional_company_filter(stmt, ProcSheetTracker, company_id)
        stmt = self.apply_proc_filter(stmt, ProcSheetTracker, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt.order_by(ProcSheetTracker.updated_at.desc())).all())

    def get(self, ctx: TenantContext, row_id: UUID) -> ProcSheetTracker | None:
        stmt = select(ProcSheetTracker).where(
            ProcSheetTracker.id == row_id,
            ProcSheetTracker.tenant_id == ctx.tenant_id,
            ProcSheetTracker.is_deleted.is_(False),
        )
        stmt = self.apply_proc_filter(stmt, ProcSheetTracker, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def create(self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object) -> ProcSheetTracker:
        row = ProcSheetTracker(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def save(self, ctx: TenantContext, row: ProcSheetTracker) -> ProcSheetTracker:
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return row
