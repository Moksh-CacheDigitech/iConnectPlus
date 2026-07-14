"""Project PrjProjectRisk repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.models import PrjProjectRisk
from modules.project.repository.base import PrjScopedRepository, utcnow


class ProjectRiskRepository(PrjScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> PrjProjectRisk | None:
        stmt = select(PrjProjectRisk).where(PrjProjectRisk.id == row_id, PrjProjectRisk.is_deleted.is_(False))
        stmt = self.apply_prj_filter(stmt, PrjProjectRisk, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select(PrjProjectRisk).where(
            PrjProjectRisk.company_id == company_id,
            PrjProjectRisk.is_deleted.is_(False),
        )
        stmt = self.apply_prj_filter(stmt, PrjProjectRisk, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> PrjProjectRisk:
        row = PrjProjectRisk(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> PrjProjectRisk | None:
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
