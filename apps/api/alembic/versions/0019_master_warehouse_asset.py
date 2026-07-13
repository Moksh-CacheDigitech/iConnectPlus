"""Create master_warehouse and master_asset tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.master_data.models.asset import MasterAsset  # noqa: F401
from modules.master_data.models.warehouse import MasterWarehouse  # noqa: F401

revision: str = "0019_master_warehouse_asset"
down_revision: str | None = "0018_master_product"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    MasterWarehouse.__table__.create(bind=bind, checkfirst=True)
    MasterAsset.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    MasterAsset.__table__.drop(bind=bind, checkfirst=True)
    MasterWarehouse.__table__.drop(bind=bind, checkfirst=True)
