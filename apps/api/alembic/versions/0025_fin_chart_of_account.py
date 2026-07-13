"""Create fin_chart_of_account table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.coa import FinChartOfAccount  # noqa: F401

revision: str = "0025_fin_chart_of_account"
down_revision: str | None = "0024_fin_account_group"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinChartOfAccount.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinChartOfAccount.__table__.drop(bind=op.get_bind(), checkfirst=True)
