"""Create proc_invoice_line table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.invoice import ProcInvoiceLine  # noqa: F401

revision: str = "0072_proc_invoice_line"
down_revision: str | None = "0071_proc_invoice_header"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcInvoiceLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcInvoiceLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
