"""Service document ORM per ERD_16 section 6.17."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceDocument(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_document"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('photo','report','contract','invoice_copy','customer_signoff','other')",
            name="ck_svc_service_document_type",
        ),
        CheckConstraint(
            "status IN ('active','superseded','archived')",
            name="ck_svc_service_document_status",
        ),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_document_contract",
        ),
        nullable=True,
        index=True,
    )
    visit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_visit.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
