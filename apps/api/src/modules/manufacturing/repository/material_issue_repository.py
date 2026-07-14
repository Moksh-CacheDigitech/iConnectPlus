"""Manufacturing MaterialIssueRepository repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgMaterialIssue, MfgMaterialIssueLine
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class MaterialIssueRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> MfgMaterialIssue | None:
        stmt = (
            select(MfgMaterialIssue)
            .options(selectinload(MfgMaterialIssue.lines))
            .where(MfgMaterialIssue.id == row_id, MfgMaterialIssue.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgMaterialIssue, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_issues(self, ctx: TenantContext, company_id: UUID):
        stmt = (
            select(MfgMaterialIssue)
            .options(selectinload(MfgMaterialIssue.lines))
            .where(MfgMaterialIssue.company_id == company_id, MfgMaterialIssue.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgMaterialIssue, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgMaterialIssue:
        row = MfgMaterialIssue(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def add_line(self, ctx: TenantContext, header: MfgMaterialIssue, **fields) -> MfgMaterialIssueLine:
        line = MfgMaterialIssueLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=header.company_id,
            branch_id=header.branch_id,
            material_issue_id=header.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(line)
        self.db.flush()
        return line

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> MfgMaterialIssue | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
