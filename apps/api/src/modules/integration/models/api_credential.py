"""API credential ORM per ERD_21 section 5.3."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntApiCredential(Base, *IntRowMixin):
    __tablename__ = "int_api_credential"
    __table_args__ = (
        UniqueConstraint("company_id", "credential_number", name="uk_int_api_credential_number"),
        CheckConstraint(
            "credential_type IN ('api_key','basic','bearer','custom_header')",
            name="ck_int_api_credential_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','expired','revoked')",
            name="ck_int_api_credential_status",
        ),
        Index("ix_int_api_cred_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    credential_number: Mapped[str] = mapped_column(String(50), nullable=False)
    external_system_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_external_system.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    credential_type: Mapped[str] = mapped_column(String(30), nullable=False)
    secret_vault_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

