"""Create fin_customer_ledger table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.ledger import FinCustomerLedger  # noqa: F401

revision: str = "0032_fin_customer_ledger"
down_revision: str | None = "0031_fin_gl_entry"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinCustomerLedger.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinCustomerLedger.__table__.drop(bind=op.get_bind(), checkfirst=True)
