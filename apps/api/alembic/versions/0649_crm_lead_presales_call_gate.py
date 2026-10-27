"""Add PreSales call alignment gate before lead BOQ/SOW routing."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from helpers import column_exists

revision: str = "0649_crm_lead_presales_call_gate"
down_revision: str | None = "0648_crm_lead_partner_contact_widen"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if not column_exists(bind, "crm_lead", "presales_call_aligned", schema="crm"):
        op.add_column(
            "crm_lead",
            sa.Column("presales_call_aligned", sa.Boolean(), nullable=True),
            schema="crm",
        )
    if not column_exists(bind, "crm_lead", "presales_call_contact_name", schema="crm"):
        op.add_column(
            "crm_lead",
            sa.Column("presales_call_contact_name", sa.String(length=150), nullable=True),
            schema="crm",
        )
    # Existing sales leads already in the BOQ/SOW pipeline stay unlocked.
    op.execute(
        """
        UPDATE crm.crm_lead
        SET presales_call_aligned = true
        WHERE company_account_id IS NOT NULL
          AND (
            boq_attached = true
            OR sow_attached = true
            OR locked = true
            OR blueprint_state <> 'open'
            OR converted_opportunity_id IS NOT NULL
          )
          AND presales_call_aligned IS NULL
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if column_exists(bind, "crm_lead", "presales_call_contact_name", schema="crm"):
        op.drop_column("crm_lead", "presales_call_contact_name", schema="crm")
    if column_exists(bind, "crm_lead", "presales_call_aligned", schema="crm"):
        op.drop_column("crm_lead", "presales_call_aligned", schema="crm")
