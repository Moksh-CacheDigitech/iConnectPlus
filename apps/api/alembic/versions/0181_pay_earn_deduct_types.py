"""Create payroll catalog type tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.payroll.models.earning_type import PayEarningType  # noqa: F401
from modules.payroll.models.deduction_type import PayDeductionType  # noqa: F401

revision: str = "0181_pay_earn_deduct_types"
down_revision: str | None = "0180_pay_payroll_period"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PayEarningType.__table__.create(bind=op.get_bind(), checkfirst=True)
    PayDeductionType.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PayDeductionType.__table__.drop(bind=op.get_bind(), checkfirst=True)
    PayEarningType.__table__.drop(bind=op.get_bind(), checkfirst=True)
