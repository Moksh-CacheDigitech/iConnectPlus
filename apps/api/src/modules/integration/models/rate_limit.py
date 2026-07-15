"""Rate limit ORM per ERD_21 section 5.17."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntRateLimit(Base, *IntRowMixin):
    __tablename__ = "int_rate_limit"
    __table_args__ = (
        UniqueConstraint("company_id", "limit_code", name="uk_int_rate_limit_code"),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_int_rate_limit_status",
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

    limit_code: Mapped[str] = mapped_column(String(50), nullable=False)

    external_system_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_external_system.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    credential_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_api_credential.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    connector_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_connector.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    max_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    burst_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
