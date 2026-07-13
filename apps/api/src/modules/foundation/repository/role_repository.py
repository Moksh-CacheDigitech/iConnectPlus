"""Role and permission repositories."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.entities import PermissionEntity, RoleEntity
from modules.foundation.models.security import SecPermission, SecRole, SecRolePermission
from modules.foundation.repository.base import TenantScopedRepository, utcnow


class RoleRepository(TenantScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, tenant_id: UUID, role_id: UUID) -> RoleEntity | None:
        stmt = (
            select(SecRole)
            .options(selectinload(SecRole.role_permissions))
            .where(
                SecRole.id == role_id,
                SecRole.tenant_id == tenant_id,
                SecRole.is_deleted.is_(False),
            )
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(self, tenant_id: UUID, role_code: str) -> SecRole | None:
        stmt = select(SecRole).where(
            SecRole.tenant_id == tenant_id,
            SecRole.role_code == role_code,
            SecRole.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def list_roles(self, tenant_id: UUID) -> list[RoleEntity]:
        stmt = (
            select(SecRole)
            .options(selectinload(SecRole.role_permissions))
            .where(SecRole.tenant_id == tenant_id, SecRole.is_deleted.is_(False))
        )
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def create(
        self,
        *,
        tenant_id: UUID,
        role_code: str,
        role_name: str,
        description: str | None = None,
        is_system_role: bool = False,
        created_by: UUID | None = None,
    ) -> RoleEntity:
        row = SecRole(
            id=uuid4(),
            tenant_id=tenant_id,
            role_code=role_code,
            role_name=role_name,
            description=description,
            is_system_role=is_system_role,
            status="active",
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(self, tenant_id: UUID, role_id: UUID, **fields: object) -> RoleEntity | None:
        row = self.get_by_id(tenant_id, role_id)
        if row is None:
            return None
        model = self.db.get(SecRole, role_id)
        assert model is not None
        for key, value in fields.items():
            if hasattr(model, key) and value is not None:
                setattr(model, key, value)
        model.updated_at = utcnow()
        self.db.flush()
        return self.get_by_id(tenant_id, role_id)

    def soft_delete(self, tenant_id: UUID, role_id: UUID, deleted_by: UUID | None = None) -> bool:
        model = self.db.get(SecRole, role_id)
        if model is None or model.tenant_id != tenant_id or model.is_deleted:
            return False
        model.is_deleted = True
        model.deleted_at = utcnow()
        model.deleted_by = deleted_by
        self.db.flush()
        return True

    def grant_permission(
        self,
        *,
        tenant_id: UUID,
        role_id: UUID,
        permission_id: UUID,
        granted_by: UUID | None,
    ) -> None:
        link = SecRolePermission(
            id=uuid4(),
            tenant_id=tenant_id,
            role_id=role_id,
            permission_id=permission_id,
            granted_at=utcnow(),
            granted_by=granted_by,
        )
        self.db.add(link)
        self.db.flush()

    @staticmethod
    def _to_entity(row: SecRole) -> RoleEntity:
        return RoleEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            role_code=row.role_code,
            role_name=row.role_name,
            status=row.status,
            is_system_role=row.is_system_role,
            description=row.description,
            permission_ids=[rp.permission_id for rp in row.role_permissions],
        )


class PermissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self, *, module: str | None = None) -> list[PermissionEntity]:
        stmt = select(SecPermission).where(SecPermission.is_active.is_(True))
        if module:
            stmt = stmt.where(SecPermission.module == module)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, permission_id: UUID) -> PermissionEntity | None:
        row = self.db.get(SecPermission, permission_id)
        return self._to_entity(row) if row else None

    def get_by_code(self, permission_code: str) -> PermissionEntity | None:
        stmt = select(SecPermission).where(SecPermission.permission_code == permission_code)
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def list_modules(self) -> list[str]:
        stmt = select(SecPermission.module).distinct()
        return sorted(self.db.scalars(stmt).all())

    @staticmethod
    def _to_entity(row: SecPermission) -> PermissionEntity:
        return PermissionEntity(
            id=row.id,
            permission_code=row.permission_code,
            resource=row.resource,
            action=row.action,
            module=row.module,
            is_active=row.is_active,
            description=row.description,
        )
