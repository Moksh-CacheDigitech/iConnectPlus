"""Create master_product_category table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.master_data.models.category import MasterProductCategory  # noqa: F401

revision: str = "0015_master_product_category"
down_revision: str | None = "0014_master_reference_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    MasterProductCategory.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    MasterProductCategory.__table__.drop(bind=bind, checkfirst=True)
