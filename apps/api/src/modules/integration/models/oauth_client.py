"""OAuth client ORM per ERD_21 section 5.4."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntOauthClient(Base, *IntRowMixin):
    __tablename__ = "int_oauth_client"
    __table_args__ = (
        UniqueConstraint("company_id", "client_number", name="uk_int_oauth_client_number"),
        CheckConstraint(
            "grant_type IN ('client_credentials','authorization_code','refresh_token')",
            name="ck_int_oauth_grant_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','revoked')",
            name="ck_int_oauth_client_status",
        ),
        Index("ix_int_oauth_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    client_number: Mapped[str] = mapped_column(String(50), nullable=False)
    external_system_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_external_system.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    client_id_public: Mapped[str] = mapped_column(String(255), nullable=False)
    client_secret_vault_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    token_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    authorize_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scopes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    grant_type: Mapped[str] = mapped_column(String(40), nullable=False)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
