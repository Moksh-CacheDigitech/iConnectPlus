"""Create SalesCustomerCredit table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.sales.models.credit import SalesCustomerCredit  # noqa: F401

revision: str = "0043_sales_customer_credit"
down_revision: str | None = "0042_sales_discount_rule"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SalesCustomerCredit.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SalesCustomerCredit.__table__.drop(bind=op.get_bind(), checkfirst=True)
