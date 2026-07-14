"""Manufacturing WIP repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgWip
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class WipRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> MfgWip | None:
        stmt = select(MfgWip).where(MfgWip.id == row_id, MfgWip.is_deleted.is_(False))
        stmt = self.apply_mfg_filter(stmt, MfgWip, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def get_by_order(self, ctx: TenantContext, production_order_id: UUID) -> MfgWip | None:
        stmt = select(MfgWip).where(
            MfgWip.production_order_id == production_order_id,
            MfgWip.is_deleted.is_(False),
        )
        stmt = self.apply_mfg_filter(stmt, MfgWip, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_wip(self, ctx: TenantContext, company_id: UUID):
        stmt = select(MfgWip).where(
            MfgWip.company_id == company_id,
            MfgWip.is_deleted.is_(False),
        )
        stmt = self.apply_mfg_filter(stmt, MfgWip, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgWip:
        row = MfgWip(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> MfgWip | None:
        row = self.get(ctx, row_id)
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
