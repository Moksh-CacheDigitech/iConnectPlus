"""Create master PostgreSQL schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0013_create_master_schema"
down_revision: str | None = "0012_sec_user_org_scope"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS master")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS master CASCADE")
