"""Leave type / balance / request services."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType, LeaveRequestStatus
from modules.hr.models import HrLeaveRequest
from modules.hr.repository.leave_balance_repository import LeaveBalanceRepository
from modules.hr.repository.leave_request_repository import LeaveRequestRepository
from modules.hr.repository.leave_type_repository import LeaveTypeRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import LeaveBalanceEngine, LeaveRequestEngine, LeaveTypeEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class LeaveTypeService:
    def __init__(self, db: Session) -> None:
        self._repo = LeaveTypeRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = LeaveTypeEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Leave type not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.create(ctx, company_id=cid, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Leave type not found")
        return row


class LeaveBalanceService:
    def __init__(self, db: Session) -> None:
        self._repo = LeaveBalanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._master = HrMasterDataAdapter(db)
        self._engine = LeaveBalanceEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Leave balance not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        opening = Decimal(str(fields.get("opening_balance", 0)))
        accrued = Decimal(str(fields.get("accrued", 0)))
        used = Decimal(str(fields.get("used", 0)))
        fields.setdefault("closing_balance", opening + accrued - used)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            **fields,
        )


class LeaveRequestService:
    def __init__(self, db: Session) -> None:
        self._repo = LeaveRequestRepository(db)
        self._balances = LeaveBalanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = LeaveRequestEngine()
        self._balance_engine = LeaveBalanceEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Leave request not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        doc = self._numbers.generate(HrEntityType.LEAVE_REQUEST, cid, HrLeaveRequest, "document_number")
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            status=fields.pop("status", LeaveRequestStatus.DRAFT.value),
            **fields,
        )

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID, *, approver_employee_id: UUID | None = None):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        balance = None
        for bal in self._balances.list_rows(ctx, row.company_id):
            if (
                bal.employee_id == row.employee_id
                and bal.leave_type_id == row.leave_type_id
                and bal.balance_year == row.start_date.year
                and bal.status == "open"
            ):
                balance = bal
                break
        if balance is None:
            raise NotFoundException("Open leave balance not found for approval year")
        self._balance_engine.apply_usage(balance, row.days_count)
        self._balances.update(
            ctx,
            balance.id,
            used=balance.used,
            closing_balance=balance.closing_balance,
        )
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            approver_employee_id=approver_employee_id,
            decided_at=datetime.now(timezone.utc),
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_leave_request",
            entity_id=row_id,
            operation="approve",
            performed_by=ctx.user_id,
        )
        return updated

    def reject(self, ctx: TenantContext, row_id: UUID, *, approver_employee_id: UUID | None = None):
        row = self.get(ctx, row_id)
        self._engine.reject(row)
        return self._repo.update(
            ctx,
            row_id,
            status=row.status,
            approver_employee_id=approver_employee_id,
            decided_at=datetime.now(timezone.utc),
        )
