"""Configuration ORM models."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from database.mixins import AuditMixin, SoftDeleteMixin, TenantMixin, VersionMixin


class CfgSetting(Base, AuditMixin, SoftDeleteMixin, TenantMixin, VersionMixin):
    __tablename__ = "cfg_setting"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "company_id",
            "branch_id",
            "setting_key",
            name="uk_cfg_setting_scope_key",
        ),
        {"schema": "config"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    branch_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    setting_key: Mapped[str] = mapped_column(String(150), nullable=False)
    setting_value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(String(30), nullable=False, default="string")
    scope: Mapped[str] = mapped_column(String(30), nullable=False, default="tenant")
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
