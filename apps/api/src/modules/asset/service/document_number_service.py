"""Asset document numbering — prefers platform SSOT, falls back to legacy sequence."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.asset.domain.enums import AstEntityType
from modules.asset.repository.code_sequence_repository import CodeSequenceRepository
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.helpers.numbering import next_document_number


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._seq = CodeSequenceRepository(db)

    def generate(
        self,
        entity: AstEntityType,
        company_id: UUID,
        model,
        code_column: str,
        *,
        ctx: TenantContext,
    ) -> str:
        prefix = getattr(entity, "value", str(entity)).upper()[:6]
        try:
            return next_document_number(
                self._db,
                tenant_id=ctx.tenant_id,
                company_id=company_id,
                sequence_key=f"asset.{getattr(entity, 'value', entity)}",
                prefix=f"{prefix}-",
                pad_width=6,
                branch_id=ctx.branch_id,
            )
        except Exception:
            return self._seq.next_code(
                entity,
                company_id,
                model=model,
                code_column=code_column,
                ctx=ctx,
            )
