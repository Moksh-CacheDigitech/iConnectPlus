"""Create EcOrderItem table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.order_item import EcOrderItem  # noqa: F401

revision: str = "0408_ec_order_item"
down_revision: str | None = "0407_ec_order"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcOrderItem.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcOrderItem.__table__.drop(bind=op.get_bind(), checkfirst=True)
