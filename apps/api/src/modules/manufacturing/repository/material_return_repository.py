"""Manufacturing MaterialReturnRepository repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgMaterialReturn, MfgMaterialReturnLine
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class MaterialReturnRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> MfgMaterialReturn | None:
        stmt = (
            select(MfgMaterialReturn)
            .options(selectinload(MfgMaterialReturn.lines))
            .where(MfgMaterialReturn.id == row_id, MfgMaterialReturn.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgMaterialReturn, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_returns(self, ctx: TenantContext, company_id: UUID):
        stmt = (
            select(MfgMaterialReturn)
            .options(selectinload(MfgMaterialReturn.lines))
            .where(MfgMaterialReturn.company_id == company_id, MfgMaterialReturn.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgMaterialReturn, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgMaterialReturn:
        row = MfgMaterialReturn(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def add_line(self, ctx: TenantContext, header: MfgMaterialReturn, **fields) -> MfgMaterialReturnLine:
        line = MfgMaterialReturnLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=header.company_id,
            branch_id=header.branch_id,
            material_return_id=header.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(line)
        self.db.flush()
        return line

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> MfgMaterialReturn | None:
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
