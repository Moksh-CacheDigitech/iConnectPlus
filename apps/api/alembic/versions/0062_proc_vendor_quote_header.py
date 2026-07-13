"""Create proc_vendor_quotation_header table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.vendor_quotation import ProcVendorQuotationHeader  # noqa: F401

revision: str = "0062_proc_vendor_quote_header"
down_revision: str | None = "0061_proc_rfq_vendor"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcVendorQuotationHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcVendorQuotationHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
