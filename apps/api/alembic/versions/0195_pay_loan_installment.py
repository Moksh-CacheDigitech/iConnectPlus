"""Create PayLoanInstallment table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.payroll.models.loan_installment import PayLoanInstallment  # noqa: F401

revision: str = "0195_pay_loan_installment"
down_revision: str | None = "0194_pay_loan"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PayLoanInstallment.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PayLoanInstallment.__table__.drop(bind=op.get_bind(), checkfirst=True)
