"""Project document numbering — platform SSOT with legacy fallback."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.project.domain.enums import PrjEntityType
from modules.project.repository.code_sequence_repository import CodeSequenceRepository
from modules.platform.helpers.ssot_numbering import generate_with_ssot


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._seq = CodeSequenceRepository(db)

    def generate(
        self,
        entity: PrjEntityType,
        company_id: UUID,
        model,
        code_column: str,
        *,
        tenant_id: UUID | None = None,
        year: int | None = None,
    ) -> str:
        key = getattr(entity, "value", str(entity))
        prefix = f"{key.upper()[:4]}-"
        return generate_with_ssot(
            self._db,
            tenant_id=tenant_id,
            company_id=company_id,
            module="project",
            entity_key=key,
            prefix=prefix,
            year=year,
            legacy=lambda: self._seq.next_code(entity, company_id, model, code_column),
        )
