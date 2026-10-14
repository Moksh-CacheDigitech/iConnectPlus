"""Sales port stub — O2C Sales module removed; CRM no longer writes sales_* tables."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext


class CrmSalesAdapter:
    """No-op adapter kept so CRM win/credit call sites stay stable without Sales."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_quotation_for_opportunity(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        customer_id: UUID,
        opportunity_id: UUID,
        currency_code: str = "USD",
    ):
        del ctx, company_id, branch_id, customer_id, opportunity_id, currency_code
        return None

    def read_customer_credit(self, ctx: TenantContext, company_id: UUID, customer_id: UUID):
        del ctx, company_id, customer_id
        return None
