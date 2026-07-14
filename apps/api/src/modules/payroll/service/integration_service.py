"""Payroll integration facade."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.adapters.hr_port import PayrollHrAdapter
from modules.payroll.adapters.master_data_port import PayrollMasterDataAdapter
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayrollIntegrationService:
    def __init__(self, db: Session) -> None:
        self._scope = PayrollScopeValidator(db)
        self._master = PayrollMasterDataAdapter(db)
        self._hr = PayrollHrAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def hr_employment_snapshot(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._hr.employment_facts(ctx, company_id)

    def hr_attendance_snapshot(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._hr.attendance_facts(ctx, company_id)

    def hr_leave_snapshot(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._hr.leave_facts(ctx, company_id)
