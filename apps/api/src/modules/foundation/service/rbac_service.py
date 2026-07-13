"""RBAC service with Redis permission cache."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.redis import SessionStore
from security.rbac import RBACEngine


class RBACService:
    def __init__(self, db: Session, session_store: SessionStore | None = None) -> None:
        self._engine = RBACEngine(db)
        self._store = session_store or SessionStore()

    def get_user_permissions(self, user_id: UUID, tenant_id: UUID) -> set[str]:
        cached = self._store.get_permissions(user_id)
        if cached is not None:
            return cached
        permissions = self._engine.get_user_permission_codes(user_id, tenant_id)
        self._store.set_permissions(user_id, permissions)
        return permissions

    def has_permission(self, user_id: UUID, tenant_id: UUID, permission_code: str) -> bool:
        return permission_code in self.get_user_permissions(user_id, tenant_id)

    def invalidate_user(self, user_id: UUID) -> None:
        self._store.invalidate_permissions(user_id)
