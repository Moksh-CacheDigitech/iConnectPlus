"""Asset AstAssetMaintenancePlan repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.asset.models import AstAssetMaintenancePlan
from modules.asset.repository.base import AstScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class AssetMaintenancePlanRepository(AstScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetMaintenancePlan | None:
        stmt = select(AstAssetMaintenancePlan).where(AstAssetMaintenancePlan.id == row_id, AstAssetMaintenancePlan.is_deleted.is_(False))
        stmt = self.apply_ast_filter(stmt, AstAssetMaintenancePlan, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select(AstAssetMaintenancePlan).where(
            AstAssetMaintenancePlan.company_id == company_id,
            AstAssetMaintenancePlan.is_deleted.is_(False),
        )
        stmt = self.apply_ast_filter(stmt, AstAssetMaintenancePlan, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> AstAssetMaintenancePlan:
        row = AstAssetMaintenancePlan(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> AstAssetMaintenancePlan | None:
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
