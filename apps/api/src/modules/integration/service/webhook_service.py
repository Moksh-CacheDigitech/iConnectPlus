"""WebhookService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.integration.domain.enums import IntegrationEntityType
from modules.integration.models import IntWebhook
from modules.integration.repository.webhook_repository import WebhookRepository
from modules.integration.service.engines import WebhookEngine
from modules.integration.service.integration_number_service import IntegrationNumberService
from modules.integration.service.integration_scope_validator import IntegrationScopeValidator


class WebhookService:
    def __init__(self, db: Session) -> None:
        self._repo = WebhookRepository(db)
        self._scope = IntegrationScopeValidator(db)
        self._numbers = IntegrationNumberService(db)
        self._engine = WebhookEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> IntWebhook:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("WebhookService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(IntegrationEntityType.WEBHOOK, cid, IntWebhook, "webhook_number")
        return self._repo.create(ctx, company_id=cid, webhook_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("WebhookService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

