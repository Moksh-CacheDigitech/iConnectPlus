"""Widen crm_lead.sub_product_category for multi-select categories."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0647_crm_lead_sub_product_category_widen"
down_revision: str | None = "0646_crm_kyc_soft_delete_cols"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "crm_lead",
        "sub_product_category",
        existing_type=sa.String(length=100),
        type_=sa.Text(),
        existing_nullable=True,
        schema="crm",
    )


def downgrade() -> None:
    op.alter_column(
        "crm_lead",
        "sub_product_category",
        existing_type=sa.Text(),
        type_=sa.String(length=100),
        existing_nullable=True,
        schema="crm",
    )
