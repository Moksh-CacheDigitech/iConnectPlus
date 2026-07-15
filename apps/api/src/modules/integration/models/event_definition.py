"""Event definition ORM per ERD_21 section 5.6."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntEventDefinition(Base, *IntRowMixin):
    __tablename__ = "int_event_definition"
    __table_args__ = (
        UniqueConstraint("company_id", "event_code", name="uk_int_event_definition_code"),
        CheckConstraint(
            "source_module IN ('foundation','finance','sales','procurement','inventory',"
            "'manufacturing','quality','crm','hr','payroll','recruitment','project','asset',"
            "'service','helpdesk','document','grc','analytics','integration','external')",
            name="ck_int_event_def_source_module",
        ),
        CheckConstraint(
            "status IN ('draft','active','deprecated')",
            name="ck_int_event_definition_status",
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

    event_code: Mapped[str] = mapped_column(String(100), nullable=False)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_module: Mapped[str] = mapped_column(String(40), nullable=False)
    payload_schema_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
