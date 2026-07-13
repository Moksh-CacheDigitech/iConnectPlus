"""Create org_branch table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.organization.models.branch import OrgBranch  # noqa: F401

revision: str = "0007_org_branch"
down_revision: str | None = "0006_org_company"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    OrgBranch.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    OrgBranch.__table__.drop(bind=bind, checkfirst=True)
