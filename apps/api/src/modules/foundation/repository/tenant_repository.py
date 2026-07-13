"""Tenant repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.entities import TenantEntity
from modules.foundation.models.security import SecTenant
from modules.foundation.repository.base import TenantScopedRepository, utcnow


class TenantRepository(TenantScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, tenant_id: UUID) -> TenantEntity | None:
        row = self.db.get(SecTenant, tenant_id)
        return self._to_entity(row) if row and not row.is_deleted else None

    def get_by_code(self, tenant_code: str) -> TenantEntity | None:
        stmt = select(SecTenant).where(
            SecTenant.tenant_code == tenant_code,
            SecTenant.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def list_all(self) -> list[TenantEntity]:
        stmt = select(SecTenant).where(SecTenant.is_deleted.is_(False))
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def create(
        self,
        *,
        tenant_code: str,
        tenant_name: str,
        created_by: UUID | None = None,
    ) -> TenantEntity:
        row = SecTenant(
            id=uuid4(),
            tenant_code=tenant_code,
            tenant_name=tenant_name,
            status="active",
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(self, tenant_id: UUID, **fields: object) -> TenantEntity | None:
        row = self.db.get(SecTenant, tenant_id)
        if row is None or row.is_deleted:
            return None
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = utcnow()
        self.db.flush()
        return self._to_entity(row)

    def soft_delete(self, tenant_id: UUID, deleted_by: UUID | None = None) -> bool:
        row = self.db.get(SecTenant, tenant_id)
        if row is None or row.is_deleted:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = deleted_by
        self.db.flush()
        return True

    @staticmethod
    def _to_entity(row: SecTenant) -> TenantEntity:
        return TenantEntity(
            id=row.id,
            tenant_code=row.tenant_code,
            tenant_name=row.tenant_name,
            status=row.status,
            timezone=row.timezone,
            locale=row.locale,
            subscription_plan=row.subscription_plan,
            max_companies=row.max_companies,
            max_users=row.max_users,
            version=row.version,
            is_deleted=row.is_deleted,
        )
