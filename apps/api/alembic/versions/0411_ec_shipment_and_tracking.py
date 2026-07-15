"""Create ec_shipment and ec_shipping_tracking tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.shipment import EcShipment  # noqa: F401
from modules.ecommerce.models.shipping_tracking import EcShippingTracking  # noqa: F401

revision: str = "0411_ec_shipment_and_tracking"
down_revision: str | None = "0410_ec_payment_transaction"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcShipment.__table__.create(bind=op.get_bind(), checkfirst=True)
    EcShippingTracking.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcShippingTracking.__table__.drop(bind=op.get_bind(), checkfirst=True)
    EcShipment.__table__.drop(bind=op.get_bind(), checkfirst=True)
