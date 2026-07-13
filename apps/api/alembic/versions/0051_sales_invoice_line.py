"""Create SalesInvoiceLine table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.sales.models.invoice import SalesInvoiceLine  # noqa: F401

revision: str = "0051_sales_invoice_line"
down_revision: str | None = "0050_sales_invoice_header"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SalesInvoiceLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SalesInvoiceLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
