"""DeadLetterService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.integration.domain.enums import IntegrationEntityType
from modules.integration.models import IntDeadLetter
from modules.integration.repository.dead_letter_repository import DeadLetterRepository
from modules.integration.service.engines import DeadLetterEngine
from modules.integration.service.integration_number_service import IntegrationNumberService
from modules.integration.service.integration_scope_validator import IntegrationScopeValidator


class DeadLetterService:
    def __init__(self, db: Session) -> None:
        self._repo = DeadLetterRepository(db)
        self._scope = IntegrationScopeValidator(db)
        self._numbers = IntegrationNumberService(db)
        self._engine = DeadLetterEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> IntDeadLetter:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("DeadLetterService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(IntegrationEntityType.DEAD_LETTER, cid, IntDeadLetter, "dlq_number")
        return self._repo.create(ctx, company_id=cid, dlq_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("DeadLetterService not found")
        return row

    def reprocess(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.reprocess(row)
        return self._repo.update(ctx, row_id, status=row.status)

