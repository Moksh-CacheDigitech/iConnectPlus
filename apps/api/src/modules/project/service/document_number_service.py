"""Project document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.project.domain.enums import PrjEntityType
from modules.project.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: PrjEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
