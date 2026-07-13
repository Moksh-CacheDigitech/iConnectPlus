"""Workflow ORM models."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from database.mixins import AuditMixin, TenantMixin


class WfDefinition(Base, AuditMixin, TenantMixin):
    __tablename__ = "wf_definition"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "workflow_code", "version_no", name="uk_wf_definition_tenant_code"
        ),
        {"schema": "foundation"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_code: Mapped[str] = mapped_column(String(100), nullable=False)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    module: Mapped[str] = mapped_column(String(50), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    steps: Mapped[list["WfStep"]] = relationship(back_populates="workflow")
    instances: Mapped[list["WfInstance"]] = relationship(back_populates="workflow")


class WfStep(Base, AuditMixin, TenantMixin):
    __tablename__ = "wf_step"
    __table_args__ = (
        UniqueConstraint("workflow_id", "step_order", name="uk_wf_step_order"),
        {"schema": "foundation"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("foundation.wf_definition.id"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_code: Mapped[str] = mapped_column(String(100), nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    approver_type: Mapped[str] = mapped_column(String(50), nullable=False)
    approver_ref: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    is_parallel: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    sla_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)

    workflow: Mapped["WfDefinition"] = relationship(back_populates="steps")
    actions: Mapped[list["WfAction"]] = relationship(back_populates="step")


class WfInstance(Base, AuditMixin, TenantMixin):
    __tablename__ = "wf_instance"
    __table_args__ = {"schema": "foundation"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("foundation.wf_definition.id"), nullable=False
    )
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    current_step_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("foundation.wf_step.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    workflow: Mapped["WfDefinition"] = relationship(back_populates="instances")
    current_step: Mapped["WfStep | None"] = relationship(foreign_keys=[current_step_id])
    actions: Mapped[list["WfAction"]] = relationship(back_populates="instance")


class WfAction(Base, TenantMixin):
    __tablename__ = "wf_action"
    __table_args__ = {"schema": "foundation"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    instance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("foundation.wf_instance.id"), nullable=False
    )
    step_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("foundation.wf_step.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    instance: Mapped["WfInstance"] = relationship(back_populates="actions")
    step: Mapped["WfStep"] = relationship(back_populates="actions")
