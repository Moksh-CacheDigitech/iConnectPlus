"""Procurement: stock ownership + open-for-sale, transfer requests, delivery milestones."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0626_proc_inventory_ownership"
down_revision: str | Sequence[str] | None = "0625_crm_ovf_live_margin"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "procurement"


def upgrade() -> None:
    for table in ("proc_inventory_stock_unit", "proc_inventory_import_line"):
        op.add_column(table, sa.Column("owner_employee_id", sa.UUID(), nullable=True), schema=_SCHEMA)
        op.add_column(table, sa.Column("owner_assigned_at", sa.DateTime(timezone=True), nullable=True), schema=_SCHEMA)
        op.add_column(table, sa.Column("source_ovf_id", sa.UUID(), nullable=True), schema=_SCHEMA)
        op.add_column(
            table,
            sa.Column("open_for_sale", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            schema=_SCHEMA,
        )
        op.add_column(table, sa.Column("open_for_sale_at", sa.DateTime(timezone=True), nullable=True), schema=_SCHEMA)
        op.create_foreign_key(
            f"fk_{table}_owner_employee",
            table,
            "master_employee",
            ["owner_employee_id"],
            ["id"],
            source_schema=_SCHEMA,
            referent_schema="master",
            ondelete="SET NULL",
        )
        op.create_index(f"ix_{table}_owner_employee_id", table, ["owner_employee_id"], schema=_SCHEMA)
        op.create_index(f"ix_{table}_source_ovf_id", table, ["source_ovf_id"], schema=_SCHEMA)

    op.add_column("proc_inventory_import_line", sa.Column("unit_cost", sa.Numeric(18, 4), nullable=True), schema=_SCHEMA)
    op.add_column("proc_inventory_import_line", sa.Column("received_on", sa.Date(), nullable=True), schema=_SCHEMA)

    op.create_table(
        "proc_inventory_transfer_request",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("requester_employee_id", sa.UUID(), nullable=False),
        sa.Column("owner_employee_id", sa.UUID(), nullable=True),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("stock_unit_ids", postgresql.JSONB(), nullable=True),
        sa.Column("import_line_ids", postgresql.JSONB(), nullable=True),
        sa.Column("customer_note", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decided_by", sa.UUID(), nullable=True),
        sa.Column("decision_remark", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["organization.org_company.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["organization.org_branch.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["requester_employee_id"], ["master.master_employee.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_employee_id"], ["master.master_employee.id"], ondelete="SET NULL"),
        sa.CheckConstraint("quantity > 0", name="ck_proc_inv_transfer_qty"),
        sa.CheckConstraint(
            "status IN ('pending','accepted','rejected','cancelled')",
            name="ck_proc_inv_transfer_status",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    for column in ("tenant_id", "company_id", "branch_id", "requester_employee_id", "owner_employee_id"):
        op.create_index(
            f"ix_proc_inventory_transfer_request_{column}",
            "proc_inventory_transfer_request",
            [column],
            schema=_SCHEMA,
        )

    op.add_column("proc_order_header", sa.Column("awb_number", sa.String(100), nullable=True), schema=_SCHEMA)
    op.add_column("proc_order_header", sa.Column("delivery_milestone", sa.String(40), nullable=True), schema=_SCHEMA)
    op.add_column(
        "proc_order_header",
        sa.Column("delivery_milestone_history", postgresql.JSONB(), nullable=True),
        schema=_SCHEMA,
    )
    op.add_column("proc_order_header", sa.Column("actual_delivery_date", sa.Date(), nullable=True), schema=_SCHEMA)
    op.create_check_constraint(
        "ck_proc_oh_delivery_milestone",
        "proc_order_header",
        "delivery_milestone IS NULL OR delivery_milestone IN ("
        "'order_placed','ready_at_factory','dispatched_from_factory','received_in_india',"
        "'received_at_warehouse','dispatched_to_site','reached_site','installed')",
        schema=_SCHEMA,
    )


def downgrade() -> None:
    op.drop_constraint("ck_proc_oh_delivery_milestone", "proc_order_header", schema=_SCHEMA, type_="check")
    for column in ("actual_delivery_date", "delivery_milestone_history", "delivery_milestone", "awb_number"):
        op.drop_column("proc_order_header", column, schema=_SCHEMA)

    op.drop_table("proc_inventory_transfer_request", schema=_SCHEMA)

    op.drop_column("proc_inventory_import_line", "received_on", schema=_SCHEMA)
    op.drop_column("proc_inventory_import_line", "unit_cost", schema=_SCHEMA)
    for table in ("proc_inventory_stock_unit", "proc_inventory_import_line"):
        op.drop_index(f"ix_{table}_source_ovf_id", table_name=table, schema=_SCHEMA)
        op.drop_index(f"ix_{table}_owner_employee_id", table_name=table, schema=_SCHEMA)
        op.drop_constraint(f"fk_{table}_owner_employee", table, schema=_SCHEMA, type_="foreignkey")
        for column in ("open_for_sale_at", "open_for_sale", "source_ovf_id", "owner_assigned_at", "owner_employee_id"):
            op.drop_column(table, column, schema=_SCHEMA)
