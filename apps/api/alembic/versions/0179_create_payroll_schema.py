"""Create payroll schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0179_create_payroll_schema"
down_revision: str | None = "0178_seed_hr_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS payroll")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS payroll CASCADE")
