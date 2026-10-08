"""Settings service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.repository.setting_repository import SettingRepository
from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.platform.data_classification import ENCRYPTED_FIELD_INVENTORY
from modules.platform.encryption import encrypt_field, mask_field, should_encrypt_field


class SettingService:
    def __init__(self, db: Session) -> None:
        self._repo = SettingRepository(db)
        self._audit = PlatformAuditFacade(db)

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
        is_encrypted: bool = False,
    ):
        store_value = setting_value
        encrypt = is_encrypted or should_encrypt_field(setting_key) or any(
            token in setting_key.lower()
            for token in ("secret", "password", "token", "api_key")
        )
        if encrypt:
            store_value = encrypt_field(setting_value) or setting_value
        setting = self._repo.upsert(
            tenant_id=tenant_id,
            setting_key=setting_key,
            setting_value=store_value,
            value_type=value_type,
            scope=scope,
            updated_by=updated_by,
        )
        if hasattr(setting, "is_encrypted"):
            setting.is_encrypted = encrypt
        audit_value = (
            mask_field(setting_value)
            if encrypt or setting_key in ENCRYPTED_FIELD_INVENTORY
            else setting_value
        )
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="cfg_setting",
            entity_id=setting.id,
            operation="update",
            performed_by=updated_by,
            new_value={setting_key: audit_value},
        )
        return setting

    def delete_setting(
        self, tenant_id: UUID, setting_key: str, deleted_by: UUID | None = None
    ) -> None:
        if not self._repo.soft_delete(tenant_id, setting_key, deleted_by=deleted_by):
            raise NotFoundException("Setting not found")
