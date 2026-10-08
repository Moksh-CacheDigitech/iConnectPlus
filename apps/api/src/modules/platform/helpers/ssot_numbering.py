"""Prefer platform document sequences; fall back to legacy next_code callables."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.helpers.numbering import next_document_number


def generate_with_ssot(
    db: Session,
    *,
    tenant_id: UUID | None,
    company_id: UUID,
    module: str,
    entity_key: str,
    prefix: str,
    pad_width: int = 6,
    year: int | None = None,
    branch_id: UUID | None = None,
    legacy: Callable[[], str],
) -> str:
    if tenant_id is None:
        return legacy()
    try:
        return next_document_number(
            db,
            tenant_id=tenant_id,
            company_id=company_id,
            sequence_key=f"{module}.{entity_key}",
            prefix=prefix,
            pad_width=pad_width,
            year=year,
            branch_id=branch_id,
        )
    except Exception:
        return legacy()
