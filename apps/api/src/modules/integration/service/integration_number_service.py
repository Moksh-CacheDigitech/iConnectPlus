"""Integration numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.integration.domain.enums import IntegrationEntityType
from modules.integration.repository.code_sequence_repository import CodeSequenceRepository


class IntegrationNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: IntegrationEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
