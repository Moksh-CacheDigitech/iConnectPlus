"""Create PostgreSQL schemas for foundation module."""

from collections.abc import Sequence

from alembic import op

revision: str = "0002_create_schemas"
down_revision: str | None = "0001_sprint0_bootstrap"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS foundation")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")
    op.execute("CREATE SCHEMA IF NOT EXISTS config")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS config CASCADE")
    op.execute("DROP SCHEMA IF EXISTS audit CASCADE")
    op.execute("DROP SCHEMA IF EXISTS foundation CASCADE")
