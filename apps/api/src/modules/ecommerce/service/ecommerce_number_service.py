"""E-Commerce numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.repository.code_sequence_repository import CodeSequenceRepository


class EcommerceNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: EcommerceEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
