"""Create PayStatutoryContribution table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.payroll.models.statutory_contribution import PayStatutoryContribution  # noqa: F401

revision: str = "0188_pay_statutory_contrib"
down_revision: str | None = "0187_pay_tax_configuration"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PayStatutoryContribution.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PayStatutoryContribution.__table__.drop(bind=op.get_bind(), checkfirst=True)
