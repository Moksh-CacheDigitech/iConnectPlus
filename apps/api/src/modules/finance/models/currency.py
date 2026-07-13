"""Currency rate ORM model."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.finance.models.mixins import FinanceMasterMixin


class FinCurrencyRate(Base, *FinanceMasterMixin):
    __tablename__ = "fin_currency_rate"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "currency_code",
            "effective_from",
            name="uk_fin_currency_rate_company_currency_date",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_fin_currency_rate_dates",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_fin_currency_rate_status",
        ),
        CheckConstraint(
            "rate_type IN ('daily','monthly','manual')",
            name="ck_fin_currency_rate_type",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    currency_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_currency.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    base_currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    rate_type: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
