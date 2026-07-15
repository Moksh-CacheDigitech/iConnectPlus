"""Create EcListingPrice table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.listing_price import EcListingPrice  # noqa: F401

revision: str = "0403_ec_listing_price"
down_revision: str | None = "0402_ec_product_listing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcListingPrice.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcListingPrice.__table__.drop(bind=op.get_bind(), checkfirst=True)
