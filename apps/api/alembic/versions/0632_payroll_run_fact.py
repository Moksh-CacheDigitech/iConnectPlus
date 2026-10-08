"""Add analytics payroll run fact read-model."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0632_payroll_run_fact"
down_revision: str | Sequence[str] | None = "0631_inventory_movement_fact"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.create_table(
        "ana_payroll_run_fact",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("payroll_run_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("gross_amount", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("net_amount", sa.Numeric(precision=18, scale=4), nullable=True),
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
        "ix_ana_payroll_run_fact_tenant_id",
        "ana_payroll_run_fact",
        ["tenant_id"],
        schema="analytics",
    )
    op.create_index(
        "ix_ana_payroll_run_fact_payroll_run_id",
        "ana_payroll_run_fact",
        ["payroll_run_id"],
        schema="analytics",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ana_payroll_run_fact_payroll_run_id",
        table_name="ana_payroll_run_fact",
        schema="analytics",
    )
    op.drop_index(
        "ix_ana_payroll_run_fact_tenant_id",
        table_name="ana_payroll_run_fact",
        schema="analytics",
    )
    op.drop_table("ana_payroll_run_fact", schema="analytics")
