"""Create MfgProductionReceipt table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.manufacturing.models.production_receipt import MfgProductionReceipt  # noqa: F401

revision: str = "0108_mfg_production_receipt"
down_revision: str | None = "0107_mfg_material_return_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    MfgProductionReceipt.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    MfgProductionReceipt.__table__.drop(bind=op.get_bind(), checkfirst=True)
