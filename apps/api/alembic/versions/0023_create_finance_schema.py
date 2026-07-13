"""Create finance PostgreSQL schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0023_create_finance_schema"
down_revision: str | None = "0022_seed_master_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS finance")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS finance CASCADE")
