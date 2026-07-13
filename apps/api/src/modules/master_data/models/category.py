"""Product category ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.master_data.models.mixins import MasterCompanyRecordMixin


class MasterProductCategory(Base, *MasterCompanyRecordMixin):
    __tablename__ = "master_product_category"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "category_code",
            name="uk_master_product_category_company_code",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_master_product_category_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    category_code: Mapped[str] = mapped_column(String(50), nullable=False)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_category_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product_category.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    level: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1")
    path: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    parent: Mapped["MasterProductCategory | None"] = relationship(
        remote_side="MasterProductCategory.id",
        foreign_keys=[parent_category_id],
    )
