"""Add soft-delete columns to crm.crm_kyc_record (SoftDeleteMixin).

Revision ID: 0646_crm_kyc_soft_delete_cols
Revises: 0645_org_company_payslip_identity
Create Date: 2026-10-27
"""

from __future__ import annotations

import sys
from pathlib import Path

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from helpers import column_exists

revision: str = "0646_crm_kyc_soft_delete_cols"
down_revision: str | None = "0645_org_company_payslip_identity"
branch_labels = None
depends_on = None

_SCHEMA = "crm"
_TABLE = "crm_kyc_record"


def upgrade() -> None:
    bind = op.get_bind()
    if not column_exists(bind, _TABLE, "deleted_at", schema=_SCHEMA):
        op.add_column(
            _TABLE,
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            schema=_SCHEMA,
        )
    if not column_exists(bind, _TABLE, "deleted_by", schema=_SCHEMA):
        op.add_column(
            _TABLE,
            sa.Column("deleted_by", PG_UUID(as_uuid=True), nullable=True),
            schema=_SCHEMA,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if column_exists(bind, _TABLE, "deleted_by", schema=_SCHEMA):
        op.drop_column(_TABLE, "deleted_by", schema=_SCHEMA)
    if column_exists(bind, _TABLE, "deleted_at", schema=_SCHEMA):
        op.drop_column(_TABLE, "deleted_at", schema=_SCHEMA)
