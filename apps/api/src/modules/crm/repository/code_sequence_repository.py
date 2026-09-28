"""CRM document code sequences via foundation patterns."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.crm.domain.enums import CODE_PREFIXES, CrmEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: CrmEntityType, company_id: UUID, model, code_column: str) -> str:
        if entity == CrmEntityType.COMPANY:
            return self._next_company_account_number(company_id, model, code_column)

        prefix, width = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-"
        # Include soft-deleted rows: the unique constraint on the code column
        # covers every row regardless of is_deleted, so a reused sequence value
        # would collide with a soft-deleted record's number.
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums: list[int] = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        seq_part = f"{seq:0{width}d}" if width > 0 else str(seq)
        return f"{full_prefix}{seq_part}"

    def next_child_code(self, parent_code: str, tag: str, company_id: UUID, model, code_column: str) -> str:
        """``{parent}/{tag}{n}`` - e.g. DR-2026-12/Q3 - counting soft-deleted rows too."""
        prefix = f"{parent_code}/{tag}"
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{prefix}%"),
        )
        seq = 0
        for code in self.db.scalars(stmt).all():
            suffix = str(code)[len(prefix) :]
            if suffix.isdigit():
                seq = max(seq, int(suffix))
        return f"{prefix}{seq + 1}"

    def _next_company_account_number(self, company_id: UUID, model, code_column: str) -> str:
        """Sales account numbers: COMP-01, COMP-02, … (per org company scope)."""
        prefix, width = CODE_PREFIXES[CrmEntityType.COMPANY]
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{prefix}%"),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums: list[int] = []
            for code in existing:
                text = str(code)
                if not text.startswith(prefix):
                    continue
                suffix = text[len(prefix) :]
                try:
                    nums.append(int(suffix))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{prefix}{seq:0{width}d}"
