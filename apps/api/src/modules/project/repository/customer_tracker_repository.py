"""Repository for versioned customer tracker files."""

from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.models.customer_tracker import PrjCustomerTracker
from modules.project.repository.base import PrjScopedRepository


class CustomerTrackerRepository(PrjScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> PrjCustomerTracker | None:
        stmt = select(PrjCustomerTracker).where(
            PrjCustomerTracker.id == row_id,
            PrjCustomerTracker.is_deleted.is_(False),
        )
        stmt = self.apply_prj_filter(stmt, PrjCustomerTracker, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID | None) -> list[PrjCustomerTracker]:
        stmt = (
            select(PrjCustomerTracker)
            .where(PrjCustomerTracker.is_deleted.is_(False))
            .order_by(PrjCustomerTracker.created_at.desc())
        )
        stmt = self.apply_optional_company_filter(stmt, PrjCustomerTracker, company_id)
        stmt = self.apply_prj_filter(stmt, PrjCustomerTracker, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def next_version(self, ctx: TenantContext, project_id: UUID) -> int:
        stmt = select(func.coalesce(func.max(PrjCustomerTracker.version_no), 0)).where(
            PrjCustomerTracker.project_id == project_id,
            PrjCustomerTracker.is_deleted.is_(False),
        )
        stmt = self.apply_prj_filter(stmt, PrjCustomerTracker, ctx, branch_scoped=True)
        return int(self.db.scalar(stmt) or 0) + 1

    def create(self, ctx: TenantContext, **fields) -> PrjCustomerTracker:
        row = PrjCustomerTracker(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row
