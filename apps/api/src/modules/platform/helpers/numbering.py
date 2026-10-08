"""Convenience wrapper for platform document numbering SSOT."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.adapters.numbering_adapter import DocumentNumberingAdapter
from modules.platform.dto import NumberRequest


def next_document_number(
    db: Session,
    *,
    tenant_id: UUID,
    company_id: UUID,
    sequence_key: str,
    prefix: str,
    pad_width: int = 6,
    year: int | None = None,
    branch_id: UUID | None = None,
) -> str:
    return DocumentNumberingAdapter(db).next_number(
        NumberRequest(
            tenant_id=tenant_id,
            company_id=company_id,
            sequence_key=sequence_key,
            prefix=prefix,
            pad_width=pad_width,
            year=year,
            branch_id=branch_id,
        )
    )
