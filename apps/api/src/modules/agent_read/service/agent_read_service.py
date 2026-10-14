"""Application services for agent read APIs."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.agent_read.repository.read_queries import (
    AgentCustomerReadRepository,
    AgentLeadReadRepository,
    AgentProductReadRepository,
)
from modules.agent_read.schemas import AgentListQuery, PaginationMeta
from modules.crm.service.crm_scope_validator import CrmScopeValidator
from modules.crm.service.lead_service import LeadService
from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.customer_service import CustomerService
from modules.master_data.service.product_service import ProductService


class AgentReadService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._crm_scope = CrmScopeValidator(db)
        self._leads = AgentLeadReadRepository(db)
        self._customers = AgentCustomerReadRepository(db)
        self._products = AgentProductReadRepository(db)
        self._lead_svc = LeadService(db)
        self._customer_svc = CustomerService(db)
        self._product_svc = ProductService(db)

    def list_leads(self, ctx: TenantContext, query: AgentListQuery):
        cid = self._crm_scope.resolve_company_id(ctx, None)
        rows, total = self._leads.search(
            ctx,
            cid,
            q=query.q,
            status=query.status,
            limit=query.limit,
            offset=query.offset,
        )
        meta = PaginationMeta(total=total, limit=query.limit, offset=query.offset)
        return rows, meta

    def get_lead(self, ctx: TenantContext, lead_id: UUID):
        return self._lead_svc.get(ctx, lead_id)

    def list_customers(self, ctx: TenantContext, query: AgentListQuery):
        rows, total = self._customers.search(
            ctx,
            q=query.q,
            status=query.status,
            limit=query.limit,
            offset=query.offset,
        )
        meta = PaginationMeta(total=total, limit=query.limit, offset=query.offset)
        return rows, meta

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        row = self._customer_svc.get_customer(ctx, customer_id)
        if row is None:
            raise NotFoundException("Customer not found")
        return row

    def list_products(self, ctx: TenantContext, query: AgentListQuery):
        rows, total = self._products.search(
            ctx,
            q=query.q,
            status=query.status,
            limit=query.limit,
            offset=query.offset,
        )
        meta = PaginationMeta(total=total, limit=query.limit, offset=query.offset)
        return rows, meta

    def get_product(self, ctx: TenantContext, product_id: UUID):
        row = self._product_svc.get_product(ctx, product_id)
        if row is None:
            raise NotFoundException("Product not found")
        return row
