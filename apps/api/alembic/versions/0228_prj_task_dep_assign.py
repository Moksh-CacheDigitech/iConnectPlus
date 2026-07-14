"""Create project graph tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.task_dependency import PrjTaskDependency  # noqa: F401
from modules.project.models.task_assignment import PrjTaskAssignment  # noqa: F401

revision: str = "0228_prj_task_dep_assign"
down_revision: str | None = "0227_prj_project_task"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    PrjTaskDependency.__table__.create(bind=op.get_bind(), checkfirst=True)
    PrjTaskAssignment.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    PrjTaskAssignment.__table__.drop(bind=op.get_bind(), checkfirst=True)
    PrjTaskDependency.__table__.drop(bind=op.get_bind(), checkfirst=True)
