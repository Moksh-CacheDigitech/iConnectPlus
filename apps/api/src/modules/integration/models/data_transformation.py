"""Data transformation ORM per ERD_21 section 5.13."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntDataTransformation(Base, *IntRowMixin):
    __tablename__ = "int_data_transformation"
    __table_args__ = (
        UniqueConstraint("mapping_id", "transformation_code", name="uk_int_data_xform_code"),
        CheckConstraint(
            "transform_type IN ('jolt','template','script_ref','expression')",
            name="ck_int_data_xform_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive')",
            name="ck_int_data_xform_status",
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

    transformation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    transformation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mapping_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_data_mapping.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    transform_type: Mapped[str] = mapped_column(String(30), nullable=False)
    definition_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
