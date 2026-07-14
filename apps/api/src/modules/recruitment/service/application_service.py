"""Application pipeline service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.domain.enums import RecEntityType
from modules.recruitment.models import RecApplication
from modules.recruitment.repository.application_repository import ApplicationRepository
from modules.recruitment.service.document_number_service import DocumentNumberService
from modules.recruitment.service.engines import ApplicationEngine
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class ApplicationService:
    def __init__(self, db: Session) -> None:
        self._repo = ApplicationRepository(db)
        self._scope = RecruitmentScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ApplicationEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> RecApplication:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Application not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(RecEntityType.APPLICATION, cid, RecApplication, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Application not found")
        return row

    def advance(self, ctx: TenantContext, row_id: UUID, *, stage: str):
        row = self.get(ctx, row_id)
        self._engine.advance(row, stage=stage)
        return self._repo.update(ctx, row_id, status=row.status, current_stage_code=row.current_stage_code)

    def reject(self, ctx: TenantContext, row_id: UUID, *, reason: str | None = None):
        row = self.get(ctx, row_id)
        self._engine.reject(row, reason=reason)
        return self._repo.update(ctx, row_id, status=row.status, rejection_reason=row.rejection_reason)
