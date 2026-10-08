"""Add analytics inventory movement fact read-model."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0631_inventory_movement_fact"
down_revision: str | Sequence[str] | None = "0630_platform_read_model"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.create_table(
        "ana_inventory_movement_fact",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_module", sa.String(length=80), nullable=False),
        sa.Column("movement_type", sa.String(length=80), nullable=False),
        sa.Column("source_document_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("warehouse_id", sa.UUID(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "projected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema="analytics",
    )
    op.create_index(
        "ix_ana_inventory_movement_fact_tenant_id",
        "ana_inventory_movement_fact",
        ["tenant_id"],
        schema="analytics",
    )
    op.create_index(
        "ix_ana_inventory_movement_fact_source_module",
        "ana_inventory_movement_fact",
        ["source_module"],
        schema="analytics",
    )
    op.create_index(
        "ix_ana_inventory_movement_fact_source_document_id",
        "ana_inventory_movement_fact",
        ["source_document_id"],
        schema="analytics",
    )
    op.create_index(
        "ix_ana_inventory_movement_fact_product_id",
        "ana_inventory_movement_fact",
        ["product_id"],
        schema="analytics",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ana_inventory_movement_fact_product_id",
        table_name="ana_inventory_movement_fact",
        schema="analytics",
    )
    op.drop_index(
        "ix_ana_inventory_movement_fact_source_document_id",
        table_name="ana_inventory_movement_fact",
        schema="analytics",
    )
    op.drop_index(
        "ix_ana_inventory_movement_fact_source_module",
        table_name="ana_inventory_movement_fact",
        schema="analytics",
    )
    op.drop_index(
        "ix_ana_inventory_movement_fact_tenant_id",
        table_name="ana_inventory_movement_fact",
        schema="analytics",
    )
    op.drop_table("ana_inventory_movement_fact", schema="analytics")
