"""Procurement: per-visit service rate contracts + plans/visits, multi-site delivery projects."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0627_proc_service_projects"
down_revision: str | Sequence[str] | None = "0626_proc_inventory_ownership"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "procurement"
_MILESTONES = (
    "'order_placed','ready_at_factory','dispatched_from_factory','received_in_india',"
    "'received_at_warehouse','dispatched_to_site','reached_site','installed'"
)


def _standard_columns() -> list[sa.Column]:
    return [
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
    ]


def _standard_fks() -> list[sa.ForeignKeyConstraint]:
    return [
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["organization.org_company.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["organization.org_branch.id"], ondelete="RESTRICT"),
    ]


def _indexes(table: str, *columns: str) -> None:
    for column in columns:
        op.create_index(f"ix_{table}_{column}", table, [column], schema=_SCHEMA)


def upgrade() -> None:
    op.create_table(
        "proc_service_rate_contract",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("contract_code", sa.String(50), nullable=False),
        sa.Column("vendor_id", sa.UUID(), nullable=True),
        sa.Column("vendor_name", sa.String(255), nullable=False),
        sa.Column("service_type", sa.String(30), nullable=False),
        sa.Column("region", sa.String(120), nullable=True),
        sa.Column("rate_per_visit", sa.Numeric(18, 4), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=False),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["vendor_id"], ["master.master_vendor.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("rate_per_visit > 0", name="ck_proc_src_rate"),
        sa.CheckConstraint(
            "service_type IN ('site_visit','installation','survey','maintenance','manpower','other')",
            name="ck_proc_src_service_type",
        ),
        sa.CheckConstraint("status IN ('active','inactive')", name="ck_proc_src_status"),
        sa.CheckConstraint("valid_to IS NULL OR valid_to >= valid_from", name="ck_proc_src_validity"),
        sa.UniqueConstraint("company_id", "contract_code", name="uk_proc_src_company_code"),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    _indexes("proc_service_rate_contract", "tenant_id", "company_id", "branch_id", "vendor_id")

    op.create_table(
        "proc_service_plan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ovf_id", sa.UUID(), nullable=False),
        sa.Column("rate_contract_id", sa.UUID(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("projected_visits", sa.Integer(), nullable=False),
        sa.Column("rate_per_visit", sa.Numeric(18, 4), nullable=False),
        sa.Column("consumables_amount", sa.Numeric(18, 4), server_default="0", nullable=False),
        sa.Column("planned_total", sa.Numeric(18, 4), nullable=False),
        sa.Column("visits_done", sa.Integer(), server_default="0", nullable=False),
        sa.Column("added_to_ovf", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("status", sa.String(20), server_default="open", nullable=False),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(
            ["rate_contract_id"], ["procurement.proc_service_rate_contract.id"], ondelete="RESTRICT"
        ),
        sa.CheckConstraint("projected_visits > 0", name="ck_proc_splan_visits"),
        sa.CheckConstraint("consumables_amount >= 0", name="ck_proc_splan_consumables"),
        sa.CheckConstraint("status IN ('open','closed')", name="ck_proc_splan_status"),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    _indexes("proc_service_plan", "tenant_id", "company_id", "branch_id", "ovf_id", "rate_contract_id")

    op.create_table(
        "proc_service_visit",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("plan_id", sa.UUID(), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("site", sa.String(255), nullable=True),
        sa.Column("engineer_name", sa.String(255), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="done", nullable=False),
        sa.Column("beyond_projection", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("expense_id", sa.UUID(), nullable=True),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["plan_id"], ["procurement.proc_service_plan.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('done','cancelled')", name="ck_proc_svisit_status"),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    _indexes("proc_service_visit", "tenant_id", "company_id", "branch_id", "plan_id")

    op.create_table(
        "proc_delivery_project",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("company_account_id", sa.UUID(), nullable=True),
        sa.Column("customer_name", sa.String(255), nullable=True),
        sa.Column("opportunity_id", sa.UUID(), nullable=True),
        sa.Column("tracking_token", sa.String(64), nullable=False),
        sa.Column("public_tracking_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("remarks", sa.Text(), nullable=True),
        *_standard_columns(),
        *_standard_fks(),
        sa.CheckConstraint("status IN ('active','on_hold','completed')", name="ck_proc_dproj_status"),
        sa.UniqueConstraint("company_id", "project_code", name="uk_proc_dproj_company_code"),
        sa.UniqueConstraint("tracking_token", name="uk_proc_dproj_tracking_token"),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    _indexes("proc_delivery_project", "tenant_id", "company_id", "branch_id", "company_account_id", "opportunity_id")

    op.create_table(
        "proc_delivery_project_site",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("circle", sa.String(120), nullable=True),
        sa.Column("site_code", sa.String(80), nullable=True),
        sa.Column("site_name", sa.String(255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("gstin", sa.String(15), nullable=True),
        sa.Column("customer_po_number", sa.String(100), nullable=True),
        sa.Column("ovf_id", sa.UUID(), nullable=True),
        sa.Column("order_header_id", sa.UUID(), nullable=True),
        sa.Column("item_summary", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=True),
        sa.Column("milestone", sa.String(40), server_default="order_placed", nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("actual_delivery_date", sa.Date(), nullable=True),
        sa.Column("awb_number", sa.String(100), nullable=True),
        sa.Column("delay_reason", sa.Text(), nullable=True),
        sa.Column("last_note", sa.Text(), nullable=True),
        sa.Column("history", postgresql.JSONB(), nullable=True),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        *_standard_columns(),
        *_standard_fks(),
        sa.ForeignKeyConstraint(["project_id"], ["procurement.proc_delivery_project.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_header_id"], ["procurement.proc_order_header.id"], ondelete="SET NULL"),
        sa.CheckConstraint(f"milestone IN ({_MILESTONES})", name="ck_proc_dsite_milestone"),
        sa.CheckConstraint(
            "status IN ('pending','in_progress','delivered','installed','on_hold','cancelled')",
            name="ck_proc_dsite_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    _indexes(
        "proc_delivery_project_site",
        "tenant_id",
        "company_id",
        "branch_id",
        "project_id",
        "ovf_id",
        "order_header_id",
    )


def downgrade() -> None:
    op.drop_table("proc_delivery_project_site", schema=_SCHEMA)
    op.drop_table("proc_delivery_project", schema=_SCHEMA)
    op.drop_table("proc_service_visit", schema=_SCHEMA)
    op.drop_table("proc_service_plan", schema=_SCHEMA)
    op.drop_table("proc_service_rate_contract", schema=_SCHEMA)
