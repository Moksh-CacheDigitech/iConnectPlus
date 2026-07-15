"""Create EcProductListing table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.product_listing import EcProductListing  # noqa: F401

revision: str = "0402_ec_product_listing"
down_revision: str | None = "0401_ec_sales_channel"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcProductListing.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcProductListing.__table__.drop(bind=op.get_bind(), checkfirst=True)
