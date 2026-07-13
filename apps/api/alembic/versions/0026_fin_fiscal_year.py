"""Create fin_fiscal_year table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.fiscal import FinFiscalYear  # noqa: F401

revision: str = "0026_fin_fiscal_year"
down_revision: str | None = "0025_fin_chart_of_account"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinFiscalYear.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinFiscalYear.__table__.drop(bind=op.get_bind(), checkfirst=True)
