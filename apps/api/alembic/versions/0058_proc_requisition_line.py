"""Create proc_requisition_line table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.requisition import ProcRequisitionLine  # noqa: F401

revision: str = "0058_proc_requisition_line"
down_revision: str | None = "0057_proc_requisition_header"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcRequisitionLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcRequisitionLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
