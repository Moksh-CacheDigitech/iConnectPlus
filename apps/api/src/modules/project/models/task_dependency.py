"""Task dependency ORM per ERD_14 §6.5."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjTaskDependency(Base, *PrjDetailMixin):
    __tablename__ = "prj_task_dependency"
    __table_args__ = (
        UniqueConstraint(
            "from_task_id", "to_task_id", "dependency_type",
            name="uk_prj_task_dep_pair_type",
        ),
        CheckConstraint("from_task_id <> to_task_id", name="ck_prj_task_dep_no_self"),
        CheckConstraint(
            "dependency_type IN ('finish_to_start','start_to_start',"
            "'finish_to_finish','start_to_finish')",
            name="ck_prj_task_dep_type",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_prj_task_dep_status"),
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    from_task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    to_task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    dependency_type: Mapped[str] = mapped_column(String(30), nullable=False, default="finish_to_start")
    lag_days: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
