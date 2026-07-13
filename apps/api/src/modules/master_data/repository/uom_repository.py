"""UOM repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import UomEntity
from modules.master_data.models.reference import MasterUom
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class UomRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_uoms(self, ctx: TenantContext, *, company_id: UUID | None = None) -> list[UomEntity]:
        stmt = select(MasterUom)
        stmt = self.apply_master_filter(stmt, MasterUom, ctx)
        if company_id:
            stmt = stmt.where(MasterUom.company_id == company_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, uom_id: UUID) -> UomEntity | None:
        stmt = select(MasterUom).where(
            MasterUom.id == uom_id,
            MasterUom.tenant_id == ctx.tenant_id,
            MasterUom.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(self, ctx: TenantContext, company_id: UUID, uom_code: str) -> MasterUom | None:
        stmt = select(MasterUom).where(
            MasterUom.tenant_id == ctx.tenant_id,
            MasterUom.company_id == company_id,
            MasterUom.uom_code == uom_code,
            MasterUom.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        uom_code: str,
        uom_name: str,
        uom_type: str,
        decimal_places: int = 2,
        is_base_uom: bool = False,
    ) -> UomEntity:
        row = MasterUom(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            uom_code=uom_code,
            uom_name=uom_name,
            uom_type=uom_type,
            decimal_places=decimal_places,
            is_base_uom=is_base_uom,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(self, ctx: TenantContext, uom_id: UUID, **fields: object) -> UomEntity | None:
        stmt = select(MasterUom).where(
            MasterUom.id == uom_id,
            MasterUom.tenant_id == ctx.tenant_id,
            MasterUom.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return self._to_entity(row)

    def soft_delete(self, ctx: TenantContext, uom_id: UUID) -> bool:
        stmt = select(MasterUom).where(
            MasterUom.id == uom_id,
            MasterUom.tenant_id == ctx.tenant_id,
        )
        row = self.db.scalar(stmt)
        if row is None or row.is_deleted:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    @staticmethod
    def _to_entity(row: MasterUom) -> UomEntity:
        return UomEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            uom_code=row.uom_code,
            uom_name=row.uom_name,
            uom_type=row.uom_type,
            decimal_places=row.decimal_places,
            is_base_uom=row.is_base_uom,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
