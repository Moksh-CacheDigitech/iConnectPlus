"""ProjectService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.project.domain.enums import PrjEntityType
from modules.project.models import PrjProject
from modules.project.repository.project_repository import ProjectRepository
from modules.project.service.document_number_service import DocumentNumberService
from modules.project.service.engines import ProjectEngine
from modules.project.service.project_scope_validator import ProjectScopeValidator


class ProjectService:
    def __init__(self, db: Session) -> None:
        self._repo = ProjectRepository(db)
        self._scope = ProjectScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ProjectEngine()
        self._audit = AuditService(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PrjProject:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("ProjectService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):

        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PrjEntityType.PROJECT, cid, PrjProject, "project_code")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, project_code=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("ProjectService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def close(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.close(row)
        return self._repo.update(ctx, row_id, status=row.status)

