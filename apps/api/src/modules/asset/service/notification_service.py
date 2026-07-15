"""NotificationService application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.asset.models import AstAssetNotification
from modules.asset.repository.asset_notification_repository import AssetNotificationRepository
from modules.asset.service.asset_scope_validator import AssetScopeValidator
from modules.asset.service.engines import AssetNotificationEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class NotificationService:
    def __init__(self, db: Session) -> None:
        self._repo = AssetNotificationRepository(db)
        self._scope = AssetScopeValidator(db)
        self._engine = AssetNotificationEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> AstAssetNotification:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("NotificationService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)

        row = self._repo.create(ctx, company_id=cid,  **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ast_asset_notification",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("NotificationService not found")
        return row
