"""Create fin_cost_center_allocation table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.allocation import FinCostCenterAllocation  # noqa: F401

revision: str = "0035_fin_cost_center_allocation"
down_revision: str | None = "0034_fin_tax_register"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinCostCenterAllocation.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinCostCenterAllocation.__table__.drop(bind=op.get_bind(), checkfirst=True)
