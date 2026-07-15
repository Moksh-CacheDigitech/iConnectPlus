"""Create EcPaymentTransaction table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.payment_transaction import EcPaymentTransaction  # noqa: F401

revision: str = "0410_ec_payment_transaction"
down_revision: str | None = "0409_ec_payment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcPaymentTransaction.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcPaymentTransaction.__table__.drop(bind=op.get_bind(), checkfirst=True)
