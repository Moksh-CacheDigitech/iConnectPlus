"""Settings service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.repository.setting_repository import SettingRepository
from modules.foundation.service.audit_service import AuditService


class SettingService:
    def __init__(self, db: Session) -> None:
        self._repo = SettingRepository(db)
        self._audit = AuditService(db)

    def list_settings(self, tenant_id: UUID):
        return self._repo.list_settings(tenant_id)

    def get_setting(self, tenant_id: UUID, setting_key: str):
        setting = self._repo.get_by_key(tenant_id, setting_key)
        if setting is None:
            raise NotFoundException("Setting not found")
        return setting

    def upsert_setting(
        self,
        *,
        tenant_id: UUID,
        setting_key: str,
        setting_value: str,
        value_type: str = "string",
        scope: str = "tenant",
        updated_by: UUID | None = None,
    ):
        setting = self._repo.upsert(
            tenant_id=tenant_id,
            setting_key=setting_key,
            setting_value=setting_value,
            value_type=value_type,
            scope=scope,
            updated_by=updated_by,
        )
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="cfg_setting",
            entity_id=setting.id,
            operation="update",
            performed_by=updated_by,
            new_value={setting_key: setting_value},
        )
        return setting

    def delete_setting(
        self, tenant_id: UUID, setting_key: str, deleted_by: UUID | None = None
    ) -> None:
        if not self._repo.soft_delete(tenant_id, setting_key, deleted_by=deleted_by):
            raise NotFoundException("Setting not found")
