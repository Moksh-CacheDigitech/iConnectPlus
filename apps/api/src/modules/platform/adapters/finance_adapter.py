"""IFinancePosting → JournalService + PostingService with idempotency."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.domain.enums import JournalStatus, JournalType
from modules.finance.repository.journal_repository import JournalRepository
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.dto import PostingResult, SystemJournalDraft
from modules.platform.models.idempotency import FndIdempotencyRecord

_SCOPE = "finance.post_system_journal"


class FinancePostingAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._journals = JournalService(db)
        self._journal_repo = JournalRepository(db)
        self._posting = PostingService(db)

    def post_system_journal(
        self,
        ctx: TenantContext,
        draft: SystemJournalDraft,
    ) -> PostingResult:
        existing = self._get_idempotent(ctx.tenant_id, draft.idempotency_key)
        if existing is not None:
            return PostingResult(
                journal_id=UUID(str(existing["journal_id"])),
                gl_entry_count=int(existing.get("gl_entry_count") or 0),
                already_posted=True,
            )

        if len(draft.lines) < 2:
            raise ValueError("System journal requires at least two lines")

        journal = self._journals.create_journal(
            ctx,
            company_id=draft.company_id,
            branch_id=draft.branch_id,
            journal_date=draft.journal_date or date.today(),
            description=draft.description,
            journal_type=JournalType.SYSTEM.value,
            fiscal_year_id=draft.fiscal_year_id,
        )
        for idx, line in enumerate(draft.lines, start=1):
            self._journals.add_line(
                ctx,
                journal.id,
                line_number=line.line_number or idx,
                account_id=line.account_id,
                debit_amount=float(line.debit_amount),
                credit_amount=float(line.credit_amount),
                description=line.description,
            )
        # PostingEngine requires APPROVED; system journals skip human workflow.
        self._journal_repo.update_journal(
            ctx, journal.id, status=JournalStatus.APPROVED.value
        )
        gl_entries = self._posting.post_system_journal(ctx, journal.id)
        result = PostingResult(
            journal_id=journal.id,
            gl_entry_count=len(gl_entries),
            already_posted=False,
        )
        self._store_idempotent(
            ctx.tenant_id,
            draft.idempotency_key,
            {
                "journal_id": str(result.journal_id),
                "gl_entry_count": result.gl_entry_count,
                "source_module": draft.source_module,
                "source_document_type": draft.source_document_type,
                "source_document_id": str(draft.source_document_id)
                if draft.source_document_id
                else None,
            },
        )
        return result

    def reverse_journal(
        self,
        ctx: TenantContext,
        journal_id: UUID,
        *,
        reason: str | None = None,
    ) -> UUID:
        """Create reversal draft (matches JournalService.reverse). Caller posts via SoD path."""
        reversal = self._journals.reverse(ctx, journal_id)
        if reason:
            reversal.description = f"{reversal.description} ({reason})"
            self._db.flush()
        return reversal.id

    def _get_idempotent(self, tenant_id: UUID, key: str) -> dict | None:
        stmt = select(FndIdempotencyRecord).where(
            FndIdempotencyRecord.tenant_id == tenant_id,
            FndIdempotencyRecord.scope == _SCOPE,
            FndIdempotencyRecord.idempotency_key == key,
        )
        row = self._db.scalars(stmt).first()
        return dict(row.result_json) if row is not None else None

    def _store_idempotent(self, tenant_id: UUID, key: str, result: dict) -> None:
        self._db.add(
            FndIdempotencyRecord(
                tenant_id=tenant_id,
                scope=_SCOPE,
                idempotency_key=key,
                result_json=result,
            )
        )
        self._db.flush()
