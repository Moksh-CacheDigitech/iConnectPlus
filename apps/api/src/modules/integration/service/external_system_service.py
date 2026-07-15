"""ExternalSystemService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.integration.domain.enums import IntegrationEntityType
from modules.integration.models import IntExternalSystem
from modules.integration.repository.external_system_repository import ExternalSystemRepository
from modules.integration.service.engines import ExternalSystemEngine
from modules.integration.service.integration_number_service import IntegrationNumberService
from modules.integration.service.integration_scope_validator import IntegrationScopeValidator


class ExternalSystemService:
    def __init__(self, db: Session) -> None:
        self._repo = ExternalSystemRepository(db)
        self._scope = IntegrationScopeValidator(db)
        self._numbers = IntegrationNumberService(db)
        self._engine = ExternalSystemEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> IntExternalSystem:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("ExternalSystemService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(IntegrationEntityType.EXTERNAL_SYSTEM, cid, IntExternalSystem, "system_number")
        return self._repo.create(ctx, company_id=cid, system_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("ExternalSystemService not found")
        return row

