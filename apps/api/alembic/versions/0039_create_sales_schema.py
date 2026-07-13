"""Create sales PostgreSQL schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0039_create_sales_schema"
down_revision: str | None = "0038_seed_finance_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS sales")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS sales CASCADE")
