"""IDocumentNumbering → platform sequence table with row lock."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.platform.dto import NumberRequest
from modules.platform.models.numbering import FndDocumentSequence


class DocumentNumberingAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def next_number(self, request: NumberRequest) -> str:
        year_bucket = request.year or 0
        stmt = (
            select(FndDocumentSequence)
            .where(
                FndDocumentSequence.tenant_id == request.tenant_id,
                FndDocumentSequence.company_id == request.company_id,
                FndDocumentSequence.sequence_key == request.sequence_key,
                FndDocumentSequence.year_bucket == year_bucket,
            )
            .with_for_update()
        )
        row = self._db.scalars(stmt).first()
        if row is None:
            row = FndDocumentSequence(
                tenant_id=request.tenant_id,
                company_id=request.company_id,
                branch_id=request.branch_id,
                sequence_key=request.sequence_key,
                prefix=request.prefix,
                pad_width=request.pad_width,
                year_bucket=year_bucket,
                next_value=1,
            )
            self._db.add(row)
            self._db.flush()
            stmt = (
                select(FndDocumentSequence)
                .where(FndDocumentSequence.id == row.id)
                .with_for_update()
            )
            row = self._db.scalars(stmt).one()

        value = row.next_value
        row.next_value = value + 1
        if request.prefix:
            row.prefix = request.prefix
        if request.pad_width:
            row.pad_width = request.pad_width
        self._db.flush()

        year_part = f"{year_bucket}-" if year_bucket else ""
        return f"{row.prefix}{year_part}{str(value).zfill(row.pad_width)}"
