"""CRM document numbering."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.crm.domain.enums import CODE_PREFIXES, CrmEntityType
from modules.crm.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: CrmEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)

    def generate_for_deal(
        self,
        entity: CrmEntityType,
        company_id: UUID,
        model,
        code_column: str,
        *,
        deal_number: str | None,
        tag: str,
    ) -> str:
        """Quotes / OVFs carry the opportunity's DR number (DR-2026-12/Q1); legacy deals keep their series."""
        dr = (deal_number or "").strip()
        if not dr:
            return self.generate(entity, company_id, model, code_column)
        return self._seq.next_child_code(dr, tag, company_id, model, code_column)

    def next_deal_reg_number(self, company_id: UUID) -> str:
        """One DR series shared by leads and opportunities (DR-YYYY-N)."""
        from modules.crm.models import CrmLead, CrmOpportunity

        prefix, width = CODE_PREFIXES[CrmEntityType.DEAL_REG]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-"
        existing: list[str] = []
        for model, column in (
            (CrmLead, CrmLead.dr_number),
            (CrmLead, CrmLead.lead_code),
            (CrmOpportunity, CrmOpportunity.deal_reg_number),
            (CrmOpportunity, CrmOpportunity.opportunity_code),
        ):
            existing.extend(
                str(code)
                for code in self._db.scalars(
                    select(column).where(
                        model.company_id == company_id,
                        column.is_not(None),
                        column.like(f"{full_prefix}%"),
                    )
                ).all()
                if code
            )
        seq = 1
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
