"""Tenant service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.foundation.repository.tenant_repository import TenantRepository
from modules.foundation.service.audit_service import AuditService


class TenantService:
    def __init__(self, db: Session) -> None:
        self._repo = TenantRepository(db)
        self._audit = AuditService(db)

    def list_tenants(self):
        return self._repo.list_all()

    def get_tenant(self, tenant_id: UUID):
        tenant = self._repo.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundException("Tenant not found")
        return tenant

    def create_tenant(self, *, tenant_code: str, tenant_name: str, created_by: UUID | None = None):
        if self._repo.get_by_code(tenant_code):
            raise ConflictException("Tenant code already exists")
        tenant = self._repo.create(
            tenant_code=tenant_code,
            tenant_name=tenant_name,
            created_by=created_by,
        )
        self._audit.log_entity_change(
            tenant_id=tenant.id,
            entity_name="sec_tenant",
            entity_id=tenant.id,
            operation="create",
            performed_by=created_by,
            new_value={"tenant_code": tenant_code, "tenant_name": tenant_name},
        )
        return tenant

    def update_tenant(self, tenant_id: UUID, updated_by: UUID | None = None, **fields):
        tenant = self._repo.update(tenant_id, **fields)
        if tenant is None:
            raise NotFoundException("Tenant not found")
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="sec_tenant",
            entity_id=tenant_id,
            operation="update",
            performed_by=updated_by,
            new_value=fields,
        )
        return tenant

    def delete_tenant(self, tenant_id: UUID, deleted_by: UUID | None = None) -> None:
        if not self._repo.soft_delete(tenant_id, deleted_by=deleted_by):
            raise NotFoundException("Tenant not found")
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="sec_tenant",
            entity_id=tenant_id,
            operation="delete",
            performed_by=deleted_by,
        )
