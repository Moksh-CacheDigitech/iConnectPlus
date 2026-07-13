"""Warehouse repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import WarehouseEntity
from modules.master_data.models.warehouse import MasterWarehouse
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class WarehouseRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_warehouses(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> list[WarehouseEntity]:
        stmt = select(MasterWarehouse)
        stmt = self.apply_master_filter(stmt, MasterWarehouse, ctx, branch_scoped=True)
        if company_id:
            stmt = stmt.where(MasterWarehouse.company_id == company_id)
        if branch_id:
            stmt = stmt.where(MasterWarehouse.branch_id == branch_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, warehouse_id: UUID) -> WarehouseEntity | None:
        stmt = select(MasterWarehouse).where(
            MasterWarehouse.id == warehouse_id,
            MasterWarehouse.tenant_id == ctx.tenant_id,
            MasterWarehouse.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(
        self, ctx: TenantContext, company_id: UUID, warehouse_code: str
    ) -> MasterWarehouse | None:
        stmt = select(MasterWarehouse).where(
            MasterWarehouse.tenant_id == ctx.tenant_id,
            MasterWarehouse.company_id == company_id,
            MasterWarehouse.warehouse_code == warehouse_code,
            MasterWarehouse.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        warehouse_code: str,
        warehouse_name: str,
        warehouse_type: str,
        location_id: UUID | None = None,
        is_default: bool = False,
        address_json: dict | None = None,
    ) -> WarehouseEntity:
        row = MasterWarehouse(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            warehouse_code=warehouse_code,
            warehouse_name=warehouse_name,
            warehouse_type=warehouse_type,
            location_id=location_id,
            is_default=is_default,
            address_json=address_json,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(
        self, ctx: TenantContext, warehouse_id: UUID, **fields: object
    ) -> WarehouseEntity | None:
        stmt = select(MasterWarehouse).where(
            MasterWarehouse.id == warehouse_id,
            MasterWarehouse.tenant_id == ctx.tenant_id,
            MasterWarehouse.is_deleted.is_(False),
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

    def soft_delete(self, ctx: TenantContext, warehouse_id: UUID) -> bool:
        stmt = select(MasterWarehouse).where(
            MasterWarehouse.id == warehouse_id,
            MasterWarehouse.tenant_id == ctx.tenant_id,
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
    def _to_entity(row: MasterWarehouse) -> WarehouseEntity:
        return WarehouseEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            branch_id=row.branch_id,
            warehouse_code=row.warehouse_code,
            warehouse_name=row.warehouse_name,
            warehouse_type=row.warehouse_type,
            location_id=row.location_id,
            is_default=row.is_default,
            address_json=row.address_json,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
