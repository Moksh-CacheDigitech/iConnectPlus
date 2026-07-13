"""Inventory adjustment repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.adjustment import InvAdjustmentHeader, InvAdjustmentLine
from modules.inventory.repository.base import InvScopedRepository, utcnow


class AdjustmentRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, adjustment_id: UUID) -> InvAdjustmentHeader | None:
        stmt = (
            select(InvAdjustmentHeader)
            .options(selectinload(InvAdjustmentHeader.lines))
            .where(
                InvAdjustmentHeader.id == adjustment_id,
                InvAdjustmentHeader.is_deleted.is_(False),
            )
        )
        stmt = self.apply_inv_filter(stmt, InvAdjustmentHeader, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_adjustments(self, ctx: TenantContext, company_id: UUID):
        stmt = (
            select(InvAdjustmentHeader)
            .options(selectinload(InvAdjustmentHeader.lines))
            .where(
                InvAdjustmentHeader.company_id == company_id,
                InvAdjustmentHeader.is_deleted.is_(False),
            )
        )
        stmt = self.apply_inv_filter(stmt, InvAdjustmentHeader, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def list_pending_finance(self, ctx: TenantContext):
        stmt = select(InvAdjustmentHeader).where(
            InvAdjustmentHeader.is_deleted.is_(False),
            InvAdjustmentHeader.status == "posted",
            InvAdjustmentHeader.finance_journal_id.is_(None),
        )
        stmt = self.apply_tenant_filter(stmt, InvAdjustmentHeader, ctx)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> InvAdjustmentHeader:
        row = InvAdjustmentHeader(
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
        self, ctx: TenantContext, header: InvAdjustmentHeader, **fields
    ) -> InvAdjustmentLine:
        line = InvAdjustmentLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=header.company_id,
            branch_id=header.branch_id,
            adjustment_header_id=header.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(line)
        self.db.flush()
        return line

    def update(
        self, ctx: TenantContext, adjustment_id: UUID, **fields
    ) -> InvAdjustmentHeader | None:
        row = self.get(ctx, adjustment_id)
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
