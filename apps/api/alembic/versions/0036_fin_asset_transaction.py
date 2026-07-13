"""Create fin_asset_transaction table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.asset import FinAssetTransaction  # noqa: F401

revision: str = "0036_fin_asset_transaction"
down_revision: str | None = "0035_fin_cost_center_allocation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinAssetTransaction.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinAssetTransaction.__table__.drop(bind=op.get_bind(), checkfirst=True)
