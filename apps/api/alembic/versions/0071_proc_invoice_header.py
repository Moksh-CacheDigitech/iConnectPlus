"""Create proc_invoice_header table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.invoice import ProcInvoiceHeader  # noqa: F401

revision: str = "0071_proc_invoice_header"
down_revision: str | None = "0070_proc_vendor_contract_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcInvoiceHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcInvoiceHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
