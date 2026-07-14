"""Create PayPayrollRunLine table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.payroll.models.payroll_run_line import PayPayrollRunLine  # noqa: F401

revision: str = "0190_pay_payroll_run_line"
down_revision: str | None = "0189_pay_payroll_run"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PayPayrollRunLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PayPayrollRunLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
