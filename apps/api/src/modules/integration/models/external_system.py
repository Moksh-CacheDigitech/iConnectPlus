"""External system ORM per ERD_21 section 5.1."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntExternalSystem(Base, *IntRowMixin):
    __tablename__ = "int_external_system"
    __table_args__ = (
        UniqueConstraint("company_id", "system_number", name="uk_int_external_system_number"),
        UniqueConstraint("company_id", "system_code", name="uk_int_external_system_code"),
        CheckConstraint(
            "system_type IN ('bank','payment_gateway','tax','ecommerce','crm_external','custom')",
            name="ck_int_external_system_type",
        ),
        CheckConstraint(
            "environment IN ('sandbox','production')",
            name="ck_int_external_system_env",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive','retired')",
            name="ck_int_external_system_status",
        ),
        Index("ix_int_ext_sys_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    system_number: Mapped[str] = mapped_column(String(50), nullable=False)
    system_code: Mapped[str] = mapped_column(String(50), nullable=False)
    system_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_type: Mapped[str] = mapped_column(String(40), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    environment: Mapped[str] = mapped_column(String(20), nullable=False, default="sandbox")

    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
