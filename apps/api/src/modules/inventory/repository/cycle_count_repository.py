"""Inventory cycle count repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.cycle_count import InvCycleCountHeader, InvCycleCountLine
from modules.inventory.repository.base import InvScopedRepository, utcnow


class CycleCountRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, count_id: UUID) -> InvCycleCountHeader | None:
        stmt = (
            select(InvCycleCountHeader)
            .options(selectinload(InvCycleCountHeader.lines))
            .where(
                InvCycleCountHeader.id == count_id,
                InvCycleCountHeader.is_deleted.is_(False),
            )
        )
        stmt = self.apply_inv_filter(stmt, InvCycleCountHeader, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_counts(self, ctx: TenantContext, company_id: UUID):
        stmt = (
            select(InvCycleCountHeader)
            .options(selectinload(InvCycleCountHeader.lines))
            .where(
                InvCycleCountHeader.company_id == company_id,
                InvCycleCountHeader.is_deleted.is_(False),
            )
        )
        stmt = self.apply_inv_filter(stmt, InvCycleCountHeader, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> InvCycleCountHeader:
        row = InvCycleCountHeader(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def add_line(
        self, ctx: TenantContext, header: InvCycleCountHeader, **fields
    ) -> InvCycleCountLine:
        line = InvCycleCountLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=header.company_id,
            branch_id=header.branch_id,
            cycle_count_header_id=header.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(line)
        self.db.flush()
        return line

    def update(self, ctx: TenantContext, count_id: UUID, **fields) -> InvCycleCountHeader | None:
        row = self.get(ctx, count_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
