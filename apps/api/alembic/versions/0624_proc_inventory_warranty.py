"""Add warranty_valid_till to procurement inventory import + stock units."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0624_proc_inventory_warranty"
down_revision: str | Sequence[str] | None = "0623_crm_lead_boq_sow_flags"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table: str, column: str, schema: str = "procurement") -> bool:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table AND column_name = :column"
        ),
        {"schema": schema, "table": table, "column": column},
    ).first()
    return rows is not None


def upgrade() -> None:
    # Column may already exist from an earlier partial apply of this work.
    if not _has_column("proc_inventory_import_line", "warranty_valid_till"):
        op.add_column(
            "proc_inventory_import_line",
            sa.Column("warranty_valid_till", sa.Date(), nullable=True),
            schema="procurement",
        )
    if not _has_column("proc_inventory_stock_unit", "warranty_valid_till"):
        op.add_column(
            "proc_inventory_stock_unit",
            sa.Column("warranty_valid_till", sa.Date(), nullable=True),
            schema="procurement",
        )


def downgrade() -> None:
    if _has_column("proc_inventory_stock_unit", "warranty_valid_till"):
        op.drop_column("proc_inventory_stock_unit", "warranty_valid_till", schema="procurement")
    if _has_column("proc_inventory_import_line", "warranty_valid_till"):
        op.drop_column("proc_inventory_import_line", "warranty_valid_till", schema="procurement")
