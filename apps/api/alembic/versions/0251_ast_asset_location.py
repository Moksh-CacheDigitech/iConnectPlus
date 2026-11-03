"""Create AstAssetLocation table.

Creates the pre-0505 shape (no location_id / building_id). Those columns and
FKs are added in 0505_ast_location_master after ast_location / ast_building exist.
Do not create from the live ORM model — it includes the later FKs.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0251_ast_asset_location"
down_revision: str | None = "0250_ast_asset_transfer"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ast_asset_location",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("branch_id", sa.Uuid(), nullable=True),
        sa.Column("asset_id", sa.Uuid(), nullable=False),
        sa.Column("location_label", sa.String(length=255), nullable=False),
        sa.Column("org_location_id", sa.Uuid(), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("company_id", sa.Uuid(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint("status IN ('active','historical')", name="ck_ast_asset_location_status"),
        sa.ForeignKeyConstraint(["asset_id"], ["asset.ast_asset.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["organization.org_branch.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["company_id"], ["organization.org_company.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        schema="asset",
        if_not_exists=True,
    )
    op.create_index(
        "ix_ast_asset_location_asset_id",
        "ast_asset_location",
        ["asset_id"],
        schema="asset",
        if_not_exists=True,
    )
    op.create_index(
        "ix_ast_asset_location_branch_id",
        "ast_asset_location",
        ["branch_id"],
        schema="asset",
        if_not_exists=True,
    )
    op.create_index(
        "ix_ast_asset_location_is_current",
        "ast_asset_location",
        ["is_current"],
        schema="asset",
        if_not_exists=True,
    )
    op.create_index(
        "ix_ast_asset_location_status",
        "ast_asset_location",
        ["status"],
        schema="asset",
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("ast_asset_location", schema="asset", if_exists=True)
