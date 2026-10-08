"""Platform document sequence SSOT."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from database.mixins import TenantMixin


class FndDocumentSequence(Base, TenantMixin):
    __tablename__ = "fnd_document_sequence"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "company_id",
            "sequence_key",
            "year_bucket",
            name="uk_fnd_document_sequence_scope",
        ),
        {"schema": "foundation"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    branch_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    sequence_key: Mapped[str] = mapped_column(String(120), nullable=False)
    prefix: Mapped[str] = mapped_column(String(40), nullable=False)
    pad_width: Mapped[int] = mapped_column(Integer, nullable=False, default=6, server_default="6")
    year_bucket: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    next_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
