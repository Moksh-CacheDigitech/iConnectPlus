"""Finance posting port — all money effects go through here."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.dto import PostingResult, SystemJournalDraft


class IFinancePosting(Protocol):
    def post_system_journal(
        self,
        ctx: TenantContext,
        draft: SystemJournalDraft,
    ) -> PostingResult:
        """Create + post a balanced system journal. Idempotent on draft.idempotency_key."""
        ...

    def reverse_journal(
        self,
        ctx: TenantContext,
        journal_id: UUID,
        *,
        reason: str | None = None,
    ) -> UUID:
        """Reverse a posted journal; returns reversal journal id."""
        ...
