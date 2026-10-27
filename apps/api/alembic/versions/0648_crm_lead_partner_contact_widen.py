"""Widen CRM lead OEM/distributor contact columns for multi-row partner tables."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0648_crm_lead_partner_contact_widen"
down_revision: str | None = "0647_crm_lead_sub_product_category_widen"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COLUMNS = (
    ("oem_contact_person", 150),
    ("oem_contact_number", 30),
    ("oem_contact_email", 255),
    ("distributor_contact", 150),
    ("distributor_contact_person", 150),
    ("distributor_contact_email", 255),
)


def upgrade() -> None:
    for column, length in _COLUMNS:
        op.alter_column(
            "crm_lead",
            column,
            existing_type=sa.String(length=length),
            type_=sa.Text(),
            existing_nullable=True,
            schema="crm",
        )


def downgrade() -> None:
    for column, length in _COLUMNS:
        op.alter_column(
            "crm_lead",
            column,
            existing_type=sa.Text(),
            type_=sa.String(length=length),
            existing_nullable=True,
            schema="crm",
        )
