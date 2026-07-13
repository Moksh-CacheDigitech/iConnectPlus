"""Settings repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.entities import SettingEntity
from modules.foundation.models.config import CfgSetting
from modules.foundation.repository.base import TenantScopedRepository, utcnow


class SettingRepository(TenantScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_settings(self, tenant_id: UUID) -> list[SettingEntity]:
        stmt = select(CfgSetting).where(
            CfgSetting.tenant_id == tenant_id,
            CfgSetting.is_deleted.is_(False),
        )
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_key(self, tenant_id: UUID, setting_key: str) -> SettingEntity | None:
        stmt = select(CfgSetting).where(
            CfgSetting.tenant_id == tenant_id,
            CfgSetting.setting_key == setting_key,
            CfgSetting.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def upsert(
        self,
        *,
        tenant_id: UUID,
        setting_key: str,
        setting_value: str,
        value_type: str = "string",
        scope: str = "tenant",
        updated_by: UUID | None = None,
    ) -> SettingEntity:
        stmt = select(CfgSetting).where(
            CfgSetting.tenant_id == tenant_id,
            CfgSetting.setting_key == setting_key,
            CfgSetting.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        if row:
            row.setting_value = setting_value
            row.value_type = value_type
            row.updated_by = updated_by
            row.updated_at = utcnow()
            row.version += 1
        else:
            row = CfgSetting(
                id=uuid4(),
                tenant_id=tenant_id,
                setting_key=setting_key,
                setting_value=setting_value,
                value_type=value_type,
                scope=scope,
                created_by=updated_by,
                updated_by=updated_by,
            )
            self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def soft_delete(
        self, tenant_id: UUID, setting_key: str, deleted_by: UUID | None = None
    ) -> bool:
        stmt = select(CfgSetting).where(
            CfgSetting.tenant_id == tenant_id,
            CfgSetting.setting_key == setting_key,
            CfgSetting.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = deleted_by
        self.db.flush()
        return True

    @staticmethod
    def _to_entity(row: CfgSetting) -> SettingEntity:
        return SettingEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            setting_key=row.setting_key,
            setting_value=row.setting_value,
            value_type=row.value_type,
            scope=row.scope,
            company_id=row.company_id,
            branch_id=row.branch_id,
            is_encrypted=row.is_encrypted,
            description=row.description,
        )
