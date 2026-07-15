"""Connector ORM per ERD_21 section 5.2."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntConnector(Base, *IntRowMixin):
    __tablename__ = "int_connector"
    __table_args__ = (
        UniqueConstraint("company_id", "connector_number", name="uk_int_connector_number"),
        CheckConstraint(
            "connector_protocol IN ('rest','webhook','queue','sftp','soap')",
            name="ck_int_connector_protocol",
        ),
        CheckConstraint(
            "direction IN ('inbound','outbound','bidirectional')",
            name="ck_int_connector_direction",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','inactive','failed','retired')",
            name="ck_int_connector_status",
        ),
        Index("ix_int_connector_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    connector_number: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_code: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_system_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_external_system.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    connector_protocol: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)

    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    credential_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_api_credential.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_int_conn_cred",
        ),
        nullable=True,
        index=True,
    )

    oauth_client_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_oauth_client.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_int_conn_oauth",
        ),
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

