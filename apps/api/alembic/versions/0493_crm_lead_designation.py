"""Add designation to crm_lead."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0493_crm_lead_designation"
down_revision = "0492_org_branch_head"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("crm_lead", schema="crm")}
    if "designation" not in cols:
        op.add_column(
            "crm_lead",
            sa.Column("designation", sa.String(length=100), nullable=True),
            schema="crm",
        )


def downgrade() -> None:
    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("crm_lead", schema="crm")}
    if "designation" in cols:
        op.drop_column("crm_lead", "designation", schema="crm")
