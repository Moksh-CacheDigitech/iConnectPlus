"""Create org_company table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from database.base import Base
from modules.organization.models.company import OrgCompany  # noqa: F401

revision: str = "0006_org_company"
down_revision: str | None = "0005_create_organization_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    OrgCompany.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    OrgCompany.__table__.drop(bind=bind, checkfirst=True)
