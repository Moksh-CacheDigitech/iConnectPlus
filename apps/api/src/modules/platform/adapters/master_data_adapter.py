"""IMasterDataLookup → master_data services."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.customer_service import CustomerService
from modules.master_data.service.product_service import ProductService
from modules.master_data.service.uom_service import UomService
from modules.master_data.service.vendor_service import VendorService
from modules.platform.dto import MasterRef


class MasterDataLookupAdapter:
    def __init__(self, db: Session) -> None:
        self._products = ProductService(db)
        self._vendors = VendorService(db)
        self._customers = CustomerService(db)
        self._uoms = UomService(db)

    def get_product(self, ctx: TenantContext, product_id: UUID) -> MasterRef:
        row = self._products.get_product(ctx, product_id)
        return MasterRef(
            id=row.id,
            code=getattr(row, "product_code", None),
            name=getattr(row, "product_name", None),
            company_id=getattr(row, "company_id", None),
        )

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID) -> MasterRef:
        row = self._vendors.get_vendor(ctx, vendor_id)
        return MasterRef(
            id=row.id,
            code=getattr(row, "vendor_code", None),
            name=getattr(row, "vendor_name", None),
            company_id=getattr(row, "company_id", None),
        )

    def get_customer(self, ctx: TenantContext, customer_id: UUID) -> MasterRef:
        row = self._customers.get_customer(ctx, customer_id)
        return MasterRef(
            id=row.id,
            code=getattr(row, "customer_code", None),
            name=getattr(row, "customer_name", None),
            company_id=getattr(row, "company_id", None),
        )

    def get_uom(self, ctx: TenantContext, uom_id: UUID) -> MasterRef:
        row = self._uoms.get_uom(ctx, uom_id)
        return MasterRef(
            id=row.id,
            code=getattr(row, "uom_code", None),
            name=getattr(row, "uom_name", None),
            company_id=getattr(row, "company_id", None),
        )
