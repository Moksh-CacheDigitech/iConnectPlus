"""Data mapping ORM per ERD_21 section 5.12."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntDataMapping(Base, *IntRowMixin):
    __tablename__ = "int_data_mapping"
    __table_args__ = (
        UniqueConstraint("company_id", "mapping_code", name="uk_int_data_mapping_code"),
        CheckConstraint(
            "status IN ('draft','active','inactive')",
            name="ck_int_data_mapping_status",
        ),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    mapping_code: Mapped[str] = mapped_column(String(50), nullable=False)
    mapping_name: Mapped[str] = mapped_column(String(255), nullable=False)
    connector_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_connector.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    source_entity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_entity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mapping_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
