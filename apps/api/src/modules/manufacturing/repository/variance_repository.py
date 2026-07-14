"""Manufacturing VarianceRepository repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgVariance
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class VarianceRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> MfgVariance | None:
        stmt = select(MfgVariance).where(MfgVariance.id == row_id, MfgVariance.is_deleted.is_(False))
        stmt = self.apply_mfg_filter(stmt, MfgVariance, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_variances(self, ctx: TenantContext, company_id: UUID):
        stmt = select(MfgVariance).where(
            MfgVariance.company_id == company_id,
            MfgVariance.is_deleted.is_(False),
        )
        stmt = self.apply_mfg_filter(stmt, MfgVariance, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgVariance:
        row = MfgVariance(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> MfgVariance | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row

    def soft_delete(self, ctx: TenantContext, row_id: UUID) -> MfgVariance | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        self.db.flush()
        return row
