"""Product category repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import CategoryEntity
from modules.master_data.models.category import MasterProductCategory
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class CategoryRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_categories(
        self, ctx: TenantContext, *, company_id: UUID | None = None
    ) -> list[CategoryEntity]:
        stmt = select(MasterProductCategory)
        stmt = self.apply_master_filter(stmt, MasterProductCategory, ctx)
        if company_id:
            stmt = stmt.where(MasterProductCategory.company_id == company_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, category_id: UUID) -> CategoryEntity | None:
        stmt = select(MasterProductCategory).where(
            MasterProductCategory.id == category_id,
            MasterProductCategory.tenant_id == ctx.tenant_id,
            MasterProductCategory.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(
        self, ctx: TenantContext, company_id: UUID, category_code: str
    ) -> MasterProductCategory | None:
        stmt = select(MasterProductCategory).where(
            MasterProductCategory.tenant_id == ctx.tenant_id,
            MasterProductCategory.company_id == company_id,
            MasterProductCategory.category_code == category_code,
            MasterProductCategory.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        category_code: str,
        category_name: str,
        parent_category_id: UUID | None = None,
        level: int = 1,
        path: str | None = None,
    ) -> CategoryEntity:
        row = MasterProductCategory(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            category_code=category_code,
            category_name=category_name,
            parent_category_id=parent_category_id,
            level=level,
            path=path,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(
        self, ctx: TenantContext, category_id: UUID, **fields: object
    ) -> CategoryEntity | None:
        stmt = select(MasterProductCategory).where(
            MasterProductCategory.id == category_id,
            MasterProductCategory.tenant_id == ctx.tenant_id,
            MasterProductCategory.is_deleted.is_(False),
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

    def soft_delete(self, ctx: TenantContext, category_id: UUID) -> bool:
        stmt = select(MasterProductCategory).where(
            MasterProductCategory.id == category_id,
            MasterProductCategory.tenant_id == ctx.tenant_id,
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
    def _to_entity(row: MasterProductCategory) -> CategoryEntity:
        return CategoryEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            category_code=row.category_code,
            category_name=row.category_name,
            parent_category_id=row.parent_category_id,
            level=row.level,
            path=row.path,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
