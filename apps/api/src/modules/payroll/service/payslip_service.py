"""Payslip application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.domain.enums import PayEntityType
from modules.payroll.models import PayPayslip
from modules.payroll.repository.payslip_repository import PayslipRepository
from modules.payroll.service.document_number_service import DocumentNumberService
from modules.payroll.service.engines import PayslipEngine
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayslipService:
    def __init__(self, db: Session) -> None:
        self._repo = PayslipRepository(db)
        self._scope = PayrollScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = PayslipEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PayPayslip:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Payslip not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PayEntityType.PAYSLIP, cid, PayPayslip, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def issue(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.issue(row)
        return self._repo.update(ctx, row_id, status=row.status)
