"""Recruitment integration facade."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.recruitment.adapters.hr_port import RecruitmentHrAdapter
from modules.recruitment.adapters.master_data_port import RecruitmentMasterDataAdapter
from modules.recruitment.adapters.organization_port import RecruitmentOrganizationAdapter
from modules.recruitment.adapters.payroll_port import RecruitmentPayrollAdapter
from modules.recruitment.service.recruitment_scope_validator import RecruitmentScopeValidator


class RecruitmentIntegrationService:
    def __init__(self, db: Session) -> None:
        self._scope = RecruitmentScopeValidator(db)
        self._master = RecruitmentMasterDataAdapter(db)
        self._org = RecruitmentOrganizationAdapter(db)
        self._hr = RecruitmentHrAdapter(db)
        self._payroll = RecruitmentPayrollAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def get_designation(self, ctx: TenantContext, designation_id: UUID):
        return self._hr.get_designation(ctx, designation_id)

    def get_salary_structure(self, ctx: TenantContext, salary_structure_id: UUID):
        return self._payroll.get_salary_structure(ctx, salary_structure_id)
