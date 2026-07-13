"""Journal posting service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import JournalType
from modules.finance.domain.exceptions import JournalStateError, SegregationOfDutiesError
from modules.finance.service.engines.posting_engine import PostingEngine
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.finance.service.journal_service import JournalService
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class PostingService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._journal_svc = JournalService(db)
        self._posting = PostingEngine(db)
        self._scope = FinanceScopeValidator(db)
        self._audit = AuditService(db)

    def post_journal(self, ctx: TenantContext, journal_id: UUID):
        journal = self._journal_svc.get_journal(ctx, journal_id)
        if journal.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot post own journal")
        return self._post(ctx, journal_id, journal)

    def post_system_journal(self, ctx: TenantContext, journal_id: UUID):
        """Post a system-generated journal, skipping segregation-of-duties."""
        journal = self._journal_svc.get_journal(ctx, journal_id)
        if journal.journal_type != JournalType.SYSTEM.value:
            raise JournalStateError("Only system journals can skip segregation of duties")
        return self._post(ctx, journal_id, journal)

    def _post(self, ctx: TenantContext, journal_id: UUID, journal):
        from modules.finance.repository.fiscal_repository import FiscalRepository
        from modules.finance.service.engines.journal_engine import JournalEngine

        period_row = FiscalRepository(self._db).get_period(ctx, journal.period_id)
        if period_row:
            JournalEngine().validate_period_for_journal(period_row, journal.journal_type)

        gl_entries = self._posting.post_journal(ctx, journal)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_journal_header",
            entity_id=journal_id,
            operation="post",
            performed_by=ctx.user_id,
            new_value={"gl_entries": len(gl_entries)},
        )
        return gl_entries
