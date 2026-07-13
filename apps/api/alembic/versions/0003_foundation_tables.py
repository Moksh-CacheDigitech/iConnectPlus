"""Create all ERD_01 foundation tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import modules.foundation.models  # noqa: F401
from database.base import Base

revision: str = "0003_foundation_tables"
down_revision: str | None = "0002_create_schemas"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_FOUNDATION_SCHEMAS = frozenset({"foundation", "audit", "config"})


def upgrade() -> None:
    bind = op.get_bind()
    for table in Base.metadata.sorted_tables:
        if table.schema in _FOUNDATION_SCHEMAS:
            table.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for table in reversed(Base.metadata.sorted_tables):
        if table.schema in _FOUNDATION_SCHEMAS:
            table.drop(bind=bind, checkfirst=True)
