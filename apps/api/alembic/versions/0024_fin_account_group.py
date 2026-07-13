"""Create fin_account_group table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.coa import FinAccountGroup  # noqa: F401

revision: str = "0024_fin_account_group"
down_revision: str | None = "0023_create_finance_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinAccountGroup.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinAccountGroup.__table__.drop(bind=op.get_bind(), checkfirst=True)
