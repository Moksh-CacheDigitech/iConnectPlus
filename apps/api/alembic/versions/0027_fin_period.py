"""Create fin_period table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.fiscal import FinPeriod  # noqa: F401

revision: str = "0027_fin_period"
down_revision: str | None = "0026_fin_fiscal_year"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinPeriod.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinPeriod.__table__.drop(bind=op.get_bind(), checkfirst=True)
