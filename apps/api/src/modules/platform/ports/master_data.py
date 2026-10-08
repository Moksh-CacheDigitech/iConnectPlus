"""Master data lookup port — SSOT for product / vendor / customer / UOM."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.dto import MasterRef


class IMasterDataLookup(Protocol):
    def get_product(self, ctx: TenantContext, product_id: UUID) -> MasterRef:
        ...

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID) -> MasterRef:
        ...

    def get_customer(self, ctx: TenantContext, customer_id: UUID) -> MasterRef:
        ...

    def get_uom(self, ctx: TenantContext, uom_id: UUID) -> MasterRef:
        ...
