"""Create master_product table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.master_data.models.product import MasterProduct  # noqa: F401

revision: str = "0018_master_product"
down_revision: str | None = "0017_master_customer_vendor"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    MasterProduct.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    MasterProduct.__table__.drop(bind=bind, checkfirst=True)
