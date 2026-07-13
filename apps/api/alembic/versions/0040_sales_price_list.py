"""Create SalesPriceList table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.sales.models.pricing import SalesPriceList  # noqa: F401

revision: str = "0040_sales_price_list"
down_revision: str | None = "0039_create_sales_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SalesPriceList.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SalesPriceList.__table__.drop(bind=op.get_bind(), checkfirst=True)
