"""Create EcPayment table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.payment import EcPayment  # noqa: F401

revision: str = "0409_ec_payment"
down_revision: str | None = "0408_ec_order_item"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcPayment.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcPayment.__table__.drop(bind=op.get_bind(), checkfirst=True)
