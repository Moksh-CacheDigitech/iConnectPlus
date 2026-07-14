"""Manufacturing BOM repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgBom, MfgBomLine
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class BomRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, bom_id: UUID) -> MfgBom | None:
        stmt = (
            select(MfgBom)
            .options(selectinload(MfgBom.lines))
            .where(MfgBom.id == bom_id, MfgBom.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgBom, ctx)
        return self.db.scalar(stmt)

    def list_boms(self, ctx: TenantContext, company_id: UUID, product_id: UUID | None = None):
        stmt = (
            select(MfgBom)
            .options(selectinload(MfgBom.lines))
            .where(MfgBom.company_id == company_id, MfgBom.is_deleted.is_(False))
        )
        if product_id is not None:
            stmt = stmt.where(MfgBom.product_id == product_id)
        stmt = self.apply_mfg_filter(stmt, MfgBom, ctx)
        return list(self.db.scalars(stmt).all())

    def find_active_for_product(
        self, ctx: TenantContext, company_id: UUID, product_id: UUID
    ) -> MfgBom | None:
        stmt = select(MfgBom).where(
            MfgBom.company_id == company_id,
            MfgBom.product_id == product_id,
            MfgBom.status == "active",
            MfgBom.is_deleted.is_(False),
        )
        stmt = self.apply_mfg_filter(stmt, MfgBom, ctx)
        return self.db.scalar(stmt)

    def create(self, ctx: TenantContext, **fields) -> MfgBom:
        row = MfgBom(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def add_line(self, ctx: TenantContext, bom: MfgBom, **fields) -> MfgBomLine:
        line = MfgBomLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=bom.company_id,
            branch_id=bom.branch_id,
            bom_id=bom.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(line)
        self.db.flush()
        return line

    def update(self, ctx: TenantContext, bom_id: UUID, **fields) -> MfgBom | None:
        row = self.get(ctx, bom_id)
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
