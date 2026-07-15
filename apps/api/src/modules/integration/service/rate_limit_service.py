"""RateLimitService application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.integration.models import IntRateLimit
from modules.integration.repository.rate_limit_repository import RateLimitRepository
from modules.integration.service.engines import RateLimitEngine
from modules.integration.service.integration_scope_validator import IntegrationScopeValidator


class RateLimitService:
    def __init__(self, db: Session) -> None:
        self._repo = RateLimitRepository(db)
        self._scope = IntegrationScopeValidator(db)
        self._engine = RateLimitEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> IntRateLimit:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("RateLimitService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        row = self._repo.create(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="int_rate_limit",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("RateLimitService not found")
        return row
