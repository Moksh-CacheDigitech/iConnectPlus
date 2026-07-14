"""Tax configuration ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayTaxConfiguration(Base, *PayMasterMixin):
    __tablename__ = "pay_tax_configuration"
    __table_args__ = (
        UniqueConstraint("company_id", "tax_config_code", name="uk_pay_tax_cfg_code"),
        CheckConstraint(
            "tax_type IN ('income_tax','professional_tax','other')",
            name="ck_pay_tax_cfg_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','archived')",
            name="ck_pay_tax_cfg_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    tax_config_code: Mapped[str] = mapped_column(String(50), nullable=False)
    tax_config_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(30), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    slabs_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
