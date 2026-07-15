"""Create EcSalesChannel table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.sales_channel import EcSalesChannel  # noqa: F401

revision: str = "0401_ec_sales_channel"
down_revision: str | None = "0400_ec_store"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcSalesChannel.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcSalesChannel.__table__.drop(bind=op.get_bind(), checkfirst=True)
