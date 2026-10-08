"""Finance document number service — platform SSOT with legacy fallback."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import FinanceEntityType
from modules.finance.repository.code_sequence_repository import CodeSequenceRepository
from modules.platform.helpers.ssot_numbering import generate_with_ssot


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = CodeSequenceRepository(db)

    def generate(
        self,
        entity_type: FinanceEntityType,
        company_id: UUID,
        *,
        model,
        code_column: str,
        year: int | None = None,
        tenant_id: UUID | None = None,
    ) -> str:
        key = getattr(entity_type, "value", str(entity_type))
        prefix = f"{key.upper()[:4]}-"
        return generate_with_ssot(
            self._db,
            tenant_id=tenant_id,
            company_id=company_id,
            module="finance",
            entity_key=key,
            prefix=prefix,
            year=year,
            legacy=lambda: self._repo.next_code(
                entity_type,
                company_id,
                model=model,
                code_column=code_column,
            ),
        )
