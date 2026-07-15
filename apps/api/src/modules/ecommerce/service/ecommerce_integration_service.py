"""E-Commerce integration service using peer adapters (C-01 + UUID refs)."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ecommerce.adapters.finance_port import EcommerceFinanceAdapter
from modules.ecommerce.adapters.integration_hub_port import EcommerceIntegrationHubAdapter
from modules.ecommerce.adapters.inventory_port import EcommerceInventoryAdapter
from modules.ecommerce.adapters.master_data_port import EcommerceMasterDataAdapter
from modules.ecommerce.adapters.organization_port import EcommerceOrganizationAdapter
from modules.ecommerce.adapters.sales_port import EcommerceSalesAdapter
from modules.ecommerce.models import EcPayment
from modules.foundation.domain.value_objects import TenantContext


class EcommerceIntegrationService:
    def __init__(self, db: Session) -> None:
        self._master = EcommerceMasterDataAdapter(db)
        self._org = EcommerceOrganizationAdapter(db)
        self._finance = EcommerceFinanceAdapter(db)
        self._sales = EcommerceSalesAdapter(db)
        self._inventory = EcommerceInventoryAdapter(db)
        self._hub = EcommerceIntegrationHubAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._master.get_customer(ctx, customer_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._master.get_product(ctx, product_id)

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID):
        return self._master.get_vendor(ctx, vendor_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def sales_order_ref(self, ctx: TenantContext, sales_order_id: UUID | None) -> UUID | None:
        return self._sales.resolve_sales_order_ref(ctx, sales_order_id)

    def inventory_item_ref(self, ctx: TenantContext, inventory_item_ref_id: UUID | None) -> UUID | None:
        return self._inventory.resolve_inventory_item_ref(ctx, inventory_item_ref_id)

    def hub_connector_ref(self, ctx: TenantContext, int_connector_id: UUID | None) -> UUID | None:
        return self._hub.resolve_connector_ref(ctx, int_connector_id)

    def hub_external_system_ref(
        self, ctx: TenantContext, int_external_system_id: UUID | None
    ) -> UUID | None:
        return self._hub.resolve_external_system_ref(ctx, int_external_system_id)

    def post_payment_capture(
        self,
        ctx: TenantContext,
        payment: EcPayment,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._finance.post_payment_capture(
            ctx,
            payment,
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )

    def post_payment_refund(
        self,
        ctx: TenantContext,
        payment: EcPayment,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._finance.post_payment_refund(
            ctx,
            payment,
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )
