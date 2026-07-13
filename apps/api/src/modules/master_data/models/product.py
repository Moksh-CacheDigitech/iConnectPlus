"""Product master ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.master_data.models.mixins import MasterCompanyRecordMixin


class MasterProduct(Base, *MasterCompanyRecordMixin):
    __tablename__ = "master_product"
    __table_args__ = (
        UniqueConstraint("company_id", "product_code", name="uk_master_product_company_code"),
        CheckConstraint(
            "product_type IN ('goods','service','bundle')",
            name="ck_master_product_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive','discontinued')",
            name="ck_master_product_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(30), nullable=False)
    category_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product_category.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    barcode: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    hsn_sac_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    standard_cost: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    list_price: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    is_inventory_tracked: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    category: Mapped["MasterProductCategory | None"] = relationship(
        foreign_keys=[category_id],
    )
    uom: Mapped["MasterUom"] = relationship(foreign_keys=[uom_id])
    tax: Mapped["MasterTax | None"] = relationship(foreign_keys=[tax_id])


from modules.master_data.models.category import MasterProductCategory  # noqa: E402
from modules.master_data.models.reference import MasterTax, MasterUom  # noqa: E402
