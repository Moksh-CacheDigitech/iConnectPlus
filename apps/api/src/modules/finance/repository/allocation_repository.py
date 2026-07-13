"""Cost center allocation repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.models.allocation import FinCostCenterAllocation
from modules.finance.repository.base import FinanceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class AllocationRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_line(self, ctx: TenantContext, journal_line_id: UUID) -> list[FinCostCenterAllocation]:
        stmt = select(FinCostCenterAllocation).where(
            FinCostCenterAllocation.journal_line_id == journal_line_id,
            FinCostCenterAllocation.tenant_id == ctx.tenant_id,
            FinCostCenterAllocation.is_deleted.is_(False),
        )
        return list(self.db.scalars(stmt).all())

    def create_allocation(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> FinCostCenterAllocation:
        row = FinCostCenterAllocation(
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

    def update_gl_entry_id(
        self, ctx: TenantContext, allocation_id: UUID, gl_entry_id: UUID
    ) -> None:
        stmt = select(FinCostCenterAllocation).where(
            FinCostCenterAllocation.id == allocation_id,
            FinCostCenterAllocation.tenant_id == ctx.tenant_id,
        )
        row = self.db.scalar(stmt)
        if row:
            row.gl_entry_id = gl_entry_id
            row.updated_at = utcnow()
            row.updated_by = ctx.user_id
            self.db.flush()
