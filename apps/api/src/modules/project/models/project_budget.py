"""Project budget ORM per ERD_14 §6.11."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectBudget(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_budget"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_bud_company_doc"),
        CheckConstraint(
            "budget_type IN ('labor','materials','travel','software','hardware','other')",
            name="ck_prj_bud_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','closed','rejected','cancelled')",
            name="ck_prj_bud_status",
        ),
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    budget_type: Mapped[str] = mapped_column(String(30), nullable=False)
    budget_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    fiscal_year_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    cost_center_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    finance_budget_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

