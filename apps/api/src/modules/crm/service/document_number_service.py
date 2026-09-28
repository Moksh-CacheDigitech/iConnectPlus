"""CRM document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.crm.domain.enums import CrmEntityType
from modules.crm.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
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
