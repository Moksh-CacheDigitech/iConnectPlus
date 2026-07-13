"""Customer credit ORM model."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.sales.models.mixins import SalesMasterMixin


class SalesCustomerCredit(Base, *SalesMasterMixin):
    __tablename__ = "sales_customer_credit"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "customer_id",
            "branch_id",
            name="uk_sales_cc_customer_branch",
        ),
        CheckConstraint("credit_limit >= 0", name="ck_sales_cc_limit"),
        CheckConstraint(
            "status IN ('active','suspended','closed')",
            name="ck_sales_cc_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    credit_limit: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    credit_used: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    credit_available: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    payment_terms_days: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    credit_hold: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    credit_hold_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
