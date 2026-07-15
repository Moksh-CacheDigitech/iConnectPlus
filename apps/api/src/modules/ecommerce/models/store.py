"""Store ORM per ERD_22 section 5.1."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcStore(Base, *EcRowMixin):
    __tablename__ = "ec_store"
    __table_args__ = (
        UniqueConstraint("company_id", "store_number", name="uk_ec_store_number"),
        UniqueConstraint("company_id", "store_code", name="uk_ec_store_code"),
        CheckConstraint(
            "store_type IN ('b2c','b2b','marketplace_brand','headless','portal')",
            name="ck_ec_store_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','inactive','retired')",
            name="ck_ec_store_status",
        ),
        Index("ix_ec_store_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    store_number: Mapped[str] = mapped_column(String(50), nullable=False)
    store_code: Mapped[str] = mapped_column(String(50), nullable=False)
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    store_type: Mapped[str] = mapped_column(String(40), nullable=False, default="b2c")
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    owner_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
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
