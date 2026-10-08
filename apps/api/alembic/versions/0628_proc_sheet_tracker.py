"""Procurement Excel sheet trackers: extracted table merged on re-upload."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0628_proc_sheet_tracker"
down_revision: str | Sequence[str] | None = "0627_proc_service_projects"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "procurement"
_TABLE = "proc_sheet_tracker"


def upgrade() -> None:
    op.create_table(
        _TABLE,
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("last_file_name", sa.String(length=180), nullable=True),
        sa.Column("column_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("row_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("columns_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rows_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("last_merge_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("last_upload_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        schema=_SCHEMA,
    )
    op.create_index("ix_proc_sheet_tracker_tenant_id", _TABLE, ["tenant_id"], schema=_SCHEMA)
    op.create_index("ix_proc_sheet_tracker_company_id", _TABLE, ["company_id"], schema=_SCHEMA)
    op.create_index("ix_proc_sheet_tracker_branch_id", _TABLE, ["branch_id"], schema=_SCHEMA)


def downgrade() -> None:
    op.drop_index("ix_proc_sheet_tracker_branch_id", table_name=_TABLE, schema=_SCHEMA)
    op.drop_index("ix_proc_sheet_tracker_company_id", table_name=_TABLE, schema=_SCHEMA)
    op.drop_index("ix_proc_sheet_tracker_tenant_id", table_name=_TABLE, schema=_SCHEMA)
    op.drop_table(_TABLE, schema=_SCHEMA)
