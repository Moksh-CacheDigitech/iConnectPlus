"""Manufacturing WorkCenterRepository repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgWorkCenter
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class WorkCenterRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> MfgWorkCenter | None:
        stmt = select(MfgWorkCenter).where(MfgWorkCenter.id == row_id, MfgWorkCenter.is_deleted.is_(False))
        stmt = self.apply_mfg_filter(stmt, MfgWorkCenter, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def list_work_centers(self, ctx: TenantContext, company_id: UUID):
        stmt = select(MfgWorkCenter).where(
            MfgWorkCenter.company_id == company_id,
            MfgWorkCenter.is_deleted.is_(False),
        )
        stmt = self.apply_mfg_filter(stmt, MfgWorkCenter, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgWorkCenter:
        row = MfgWorkCenter(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> MfgWorkCenter | None:
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

    def soft_delete(self, ctx: TenantContext, row_id: UUID) -> MfgWorkCenter | None:
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
