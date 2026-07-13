"""Cost center allocation service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.finance.domain.enums import JournalStatus
from modules.finance.repository.allocation_repository import AllocationRepository
from modules.finance.repository.journal_repository import JournalRepository
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext


class CostAllocationService:
    def __init__(self, db: Session) -> None:
        self._repo = AllocationRepository(db)
        self._journal = JournalRepository(db)
        self._scope = FinanceScopeValidator(db)

    def list_allocations(self, ctx: TenantContext, journal_line_id: UUID):
        return self._repo.list_for_line(ctx, journal_line_id)

    def create_allocation(
        self,
        ctx: TenantContext,
        journal_line_id: UUID,
        *,
        cost_center_id: UUID,
        allocation_sequence: int,
        allocated_amount: float,
        allocation_percent: float | None = None,
        description: str | None = None,
    ):
        line = self._journal.get_line(ctx, journal_line_id)
        if line is None:
            raise NotFoundException("Journal line not found")
        journal = self._journal.get_journal(ctx, line.journal_header_id)
        if journal is None or journal.status != JournalStatus.DRAFT.value:
            raise ConflictException("Allocations only allowed on draft journal lines")

        existing = self._repo.list_for_line(ctx, journal_line_id)
        total_allocated = sum(Decimal(str(a.allocated_amount)) for a in existing)
        total_allocated += Decimal(str(allocated_amount))
        line_amount = Decimal(str(line.debit_amount or line.credit_amount))
        if total_allocated > line_amount:
            raise ConflictException("Total allocation exceeds line amount")

        return self._repo.create_allocation(
            ctx,
            company_id=line.company_id,
            branch_id=line.branch_id,
            journal_line_id=journal_line_id,
            cost_center_id=cost_center_id,
            allocation_sequence=allocation_sequence,
            allocated_amount=allocated_amount,
            allocation_percent=allocation_percent,
            description=description,
        )
