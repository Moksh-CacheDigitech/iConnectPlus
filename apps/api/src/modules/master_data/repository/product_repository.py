"""Product repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import ProductEntity
from modules.master_data.models.product import MasterProduct
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class ProductRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_products(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID | None = None,
    ) -> list[ProductEntity]:
        stmt = select(MasterProduct)
        stmt = self.apply_master_filter(stmt, MasterProduct, ctx)
        if company_id:
            stmt = stmt.where(MasterProduct.company_id == company_id)
        if branch_id:
            stmt = stmt.where(MasterProduct.branch_id == branch_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, product_id: UUID) -> ProductEntity | None:
        stmt = select(MasterProduct).where(
            MasterProduct.id == product_id,
            MasterProduct.tenant_id == ctx.tenant_id,
            MasterProduct.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(
        self, ctx: TenantContext, company_id: UUID, product_code: str
    ) -> MasterProduct | None:
        stmt = select(MasterProduct).where(
            MasterProduct.tenant_id == ctx.tenant_id,
            MasterProduct.company_id == company_id,
            MasterProduct.product_code == product_code,
            MasterProduct.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        product_code: str,
        product_name: str,
        product_type: str,
        uom_id: UUID,
        branch_id: UUID | None = None,
        category_id: UUID | None = None,
        tax_id: UUID | None = None,
        barcode: str | None = None,
        is_inventory_tracked: bool = True,
    ) -> ProductEntity:
        row = MasterProduct(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            product_code=product_code,
            product_name=product_name,
            product_type=product_type,
            uom_id=uom_id,
            category_id=category_id,
            tax_id=tax_id,
            barcode=barcode,
            is_inventory_tracked=is_inventory_tracked,
            status="draft",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(
        self, ctx: TenantContext, product_id: UUID, **fields: object
    ) -> ProductEntity | None:
        stmt = select(MasterProduct).where(
            MasterProduct.id == product_id,
            MasterProduct.tenant_id == ctx.tenant_id,
            MasterProduct.is_deleted.is_(False),
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

    def soft_delete(self, ctx: TenantContext, product_id: UUID) -> bool:
        stmt = select(MasterProduct).where(
            MasterProduct.id == product_id,
            MasterProduct.tenant_id == ctx.tenant_id,
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
    def _to_entity(row: MasterProduct) -> ProductEntity:
        return ProductEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            product_code=row.product_code,
            product_name=row.product_name,
            product_type=row.product_type,
            uom_id=row.uom_id,
            branch_id=row.branch_id,
            category_id=row.category_id,
            tax_id=row.tax_id,
            barcode=row.barcode,
            is_inventory_tracked=row.is_inventory_tracked,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
