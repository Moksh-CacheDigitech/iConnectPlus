"""Webhook ORM per ERD_21 section 5.5."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntWebhook(Base, *IntRowMixin):
    __tablename__ = "int_webhook"
    __table_args__ = (
        UniqueConstraint("company_id", "webhook_number", name="uk_int_webhook_number"),
        CheckConstraint(
            "direction IN ('inbound','outbound')",
            name="ck_int_webhook_direction",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','paused','retired')",
            name="ck_int_webhook_status",
        ),
        Index("ix_int_webhook_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    webhook_number: Mapped[str] = mapped_column(String(50), nullable=False)

    external_system_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_external_system.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    connector_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_connector.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)

    event_definition_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_event_definition.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_int_wh_event_def",
        ),
        nullable=True,
        index=True,
    )
    secret_vault_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

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

