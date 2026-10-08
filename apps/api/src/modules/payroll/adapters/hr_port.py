"""HR port - wraps HRIntegrationService payroll read facts."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.models.employee_profile import HrEmployeeProfile
from modules.hr.service.integration_service import HRIntegrationService


class PayrollHrAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._hr = HRIntegrationService(db)

    def bank_details(self, employee_id: UUID) -> dict[str, str | None]:
        profile = self._db.scalar(
            select(HrEmployeeProfile).where(
                HrEmployeeProfile.employee_id == employee_id,
                HrEmployeeProfile.is_deleted.is_(False),
            )
        )
        if profile is None:
            return {"account_number": None, "ifsc": None, "bank_name": None, "account_holder": None}
        return {
            "account_number": getattr(profile, "bank_account_number", None),
            "ifsc": getattr(profile, "bank_ifsc", None),
            "bank_name": getattr(profile, "bank_name", None),
            "account_holder": getattr(profile, "bank_account_holder", None),
        }

    def employment_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        return self._hr.payroll_employment_facts(ctx, company_id)

    def attendance_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        return self._hr.payroll_attendance_facts(ctx, company_id)

    def leave_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        return self._hr.payroll_leave_facts(ctx, company_id)
