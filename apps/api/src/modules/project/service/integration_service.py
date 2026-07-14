"""Project integration service â€” cross-module reads only."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.adapters.master_data_port import ProjectMasterDataAdapter
from modules.project.adapters.organization_port import ProjectOrganizationAdapter
from modules.project.adapters.payroll_port import ProjectPayrollAdapter


class ProjectIntegrationService:
    def __init__(self, db: Session) -> None:
        self._master = ProjectMasterDataAdapter(db)
        self._org = ProjectOrganizationAdapter(db)
        self._payroll = ProjectPayrollAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._master.get_customer(ctx, customer_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._master.get_product(ctx, product_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def labor_cost_hint(self, ctx: TenantContext, employee_id: UUID):
        return self._payroll.labor_cost_hint(ctx, employee_id)
