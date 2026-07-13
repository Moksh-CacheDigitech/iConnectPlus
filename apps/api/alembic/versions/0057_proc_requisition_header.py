"""Create proc_requisition_header table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.requisition import ProcRequisitionHeader  # noqa: F401

revision: str = "0057_proc_requisition_header"
down_revision: str | None = "0056_create_procurement_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcRequisitionHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcRequisitionHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
