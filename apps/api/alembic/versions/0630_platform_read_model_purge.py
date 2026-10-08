"""Platform read-model fact table in analytics schema."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0630_platform_read_model"
down_revision: str | Sequence[str] | None = "0629_fnd_platform_outbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.create_table(
        "ana_finance_posting_fact",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_module", sa.String(length=80), nullable=False),
        sa.Column("source_document_type", sa.String(length=80), nullable=False),
        sa.Column("source_document_id", sa.UUID(), nullable=False),
        sa.Column("journal_id", sa.UUID(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=True),
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
        "ix_ana_finance_posting_fact_tenant_id",
        "ana_finance_posting_fact",
        ["tenant_id"],
        schema="analytics",
    )
    op.create_index(
        "ix_ana_finance_posting_fact_source_module",
        "ana_finance_posting_fact",
        ["source_module"],
        schema="analytics",
    )
    op.create_index(
        "ix_ana_finance_posting_fact_source_document_id",
        "ana_finance_posting_fact",
        ["source_document_id"],
        schema="analytics",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ana_finance_posting_fact_source_document_id",
        table_name="ana_finance_posting_fact",
        schema="analytics",
    )
    op.drop_index(
        "ix_ana_finance_posting_fact_source_module",
        table_name="ana_finance_posting_fact",
        schema="analytics",
    )
    op.drop_index(
        "ix_ana_finance_posting_fact_tenant_id",
        table_name="ana_finance_posting_fact",
        schema="analytics",
    )
    op.drop_table("ana_finance_posting_fact", schema="analytics")
