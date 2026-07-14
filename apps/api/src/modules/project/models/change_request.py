"""Change request ORM per ERD_14 §6.15."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjChangeRequest(Base, *PrjTransactionMixin):
    __tablename__ = "prj_change_request"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_cr_company_doc"),
        CheckConstraint(
            "change_type IN ('scope','schedule','budget','resource','other')",
            name="ck_prj_cr_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','rejected','implemented','cancelled')",
            name="ck_prj_cr_status",
        ),
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    change_title: Mapped[str] = mapped_column(String(255), nullable=False)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    requested_by_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    impact_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_impact_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    schedule_impact_days: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

