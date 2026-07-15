"""Create SvcServiceCategory table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.models.service_category import SvcServiceCategory  # noqa: F401

revision: str = "0268_svc_service_category"
down_revision: str | None = "0267_create_service_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SvcServiceCategory.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SvcServiceCategory.__table__.drop(bind=op.get_bind(), checkfirst=True)
