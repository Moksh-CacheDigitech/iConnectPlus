"""Generate Sprint 22 E-Commerce / External Channel module. Run from apps/api:
.venv\\Scripts\\python.exe scripts/_gen_ecommerce_module.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ECOMMERCE = SRC / "modules" / "ecommerce"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []

WF_FIELDS = """
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
"""

OPT_BRANCH = """
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
"""


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    FILES_WRITTEN.append(path)
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new.strip() in text:
        print("skip (already)", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"patch failed in {path}: marker not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


# table_key, ORM class, stem, branch_scoped
TABLES: list[tuple[str, str, str, bool]] = [
    ("store", "EcStore", "Store", False),
    ("sales_channel", "EcSalesChannel", "SalesChannel", False),
    ("product_listing", "EcProductListing", "ProductListing", False),
    ("listing_price", "EcListingPrice", "ListingPrice", False),
    ("listing_inventory", "EcListingInventory", "ListingInventory", False),
    ("customer_cart", "EcCustomerCart", "CustomerCart", False),
    ("cart_item", "EcCartItem", "CartItem", False),
    ("order", "EcOrder", "Order", False),
    ("order_item", "EcOrderItem", "OrderItem", False),
    ("payment", "EcPayment", "Payment", False),
    ("payment_transaction", "EcPaymentTransaction", "PaymentTransaction", False),
    ("shipment", "EcShipment", "Shipment", False),
    ("shipping_tracking", "EcShippingTracking", "ShippingTracking", False),
    ("return_request", "EcReturnRequest", "ReturnRequest", False),
    ("return_item", "EcReturnItem", "ReturnItem", False),
    ("coupon", "EcCoupon", "Coupon", False),
    ("promotion", "EcPromotion", "Promotion", False),
    ("marketplace_connector", "EcMarketplaceConnector", "MarketplaceConnector", False),
    ("notification", "EcNotification", "Notification", False),
    ("report", "EcReport", "Report", False),
]


CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0399_create_ecommerce_schema", "schema", "0398_seed_integration_workflows"),
    ("0400_ec_store", "store", "0399_create_ecommerce_schema"),
    ("0401_ec_sales_channel", "sales_channel", "0400_ec_store"),
    ("0402_ec_product_listing", "product_listing", "0401_ec_sales_channel"),
    ("0403_ec_listing_price", "listing_price", "0402_ec_product_listing"),
    ("0404_ec_listing_inventory", "listing_inventory", "0403_ec_listing_price"),
    ("0405_ec_customer_cart", "customer_cart", "0404_ec_listing_inventory"),
    ("0406_ec_cart_item", "cart_item", "0405_ec_customer_cart"),
    ("0407_ec_order", "order", "0406_ec_cart_item"),
    ("0408_ec_order_item", "order_item", "0407_ec_order"),
    ("0409_ec_payment", "payment", "0408_ec_order_item"),
    ("0410_ec_payment_transaction", "payment_transaction", "0409_ec_payment"),
    ("0411_ec_shipment_and_tracking", ["shipment", "shipping_tracking"], "0410_ec_payment_transaction"),
    ("0412_ec_return_request", "return_request", "0411_ec_shipment_and_tracking"),
    ("0413_ec_return_item", "return_item", "0412_ec_return_request"),
    ("0414_ec_coupon", "coupon", "0413_ec_return_item"),
    ("0415_ec_promotion", "promotion", "0414_ec_coupon"),
    ("0416_ec_marketplace_connector", "marketplace_connector", "0415_ec_promotion"),
    ("0417_ec_notification", "notification", "0416_ec_marketplace_connector"),
    ("0418_ec_report", "report", "0417_ec_notification"),
    ("0419_seed_ec_permissions", "seed_perms", "0418_ec_report"),
    ("0420_seed_ecommerce_workflows", "seed_wf", "0419_seed_ec_permissions"),
]


# route prefix, schema name, service class, perm resource, branch_required
ROUTE_SPECS: list[tuple[str, str, str, str, bool]] = [
    ("stores", "Store", "StoreService", "ecommerce.store", False),
    ("sales-channels", "SalesChannel", "SalesChannelService", "ecommerce.channel", False),
    ("product-listings", "ProductListing", "ProductListingService", "ecommerce.listing", False),
    ("listing-prices", "ListingPrice", "ListingPriceService", "ecommerce.price", False),
    ("listing-inventories", "ListingInventory", "ListingInventoryService", "ecommerce.listing_inventory", False),
    ("customer-carts", "CustomerCart", "CustomerCartService", "ecommerce.cart", False),
    ("cart-items", "CartItem", "CartItemService", "ecommerce.cart", False),
    ("orders", "Order", "OrderService", "ecommerce.order", False),
    ("order-items", "OrderItem", "OrderItemService", "ecommerce.order", False),
    ("payments", "Payment", "PaymentService", "ecommerce.payment", False),
    ("payment-transactions", "PaymentTransaction", "PaymentTransactionService", "ecommerce.payment_txn", False),
    ("shipments", "Shipment", "ShipmentService", "ecommerce.shipment", False),
    ("shipping-trackings", "ShippingTracking", "ShippingTrackingService", "ecommerce.tracking", False),
    ("return-requests", "ReturnRequest", "ReturnRequestService", "ecommerce.return", False),
    ("return-items", "ReturnItem", "ReturnItemService", "ecommerce.return", False),
    ("coupons", "Coupon", "CouponService", "ecommerce.coupon", False),
    ("promotions", "Promotion", "PromotionService", "ecommerce.promotion", False),
    ("marketplace-connectors", "MarketplaceConnector", "MarketplaceConnectorService", "ecommerce.marketplace", False),
    ("notifications", "Notification", "NotificationService", "ecommerce.notification", False),
    ("reports", "Report", "ReportService", "ecommerce.report", False),
]



ENGINE_NAMES = [
    "Store",
    "SalesChannel",
    "ProductListing",
    "ListingPrice",
    "ListingInventory",
    "CustomerCart",
    "CartItem",
    "Order",
    "OrderItem",
    "Payment",
    "PaymentTransaction",
    "Shipment",
    "ShippingTracking",
    "ReturnRequest",
    "ReturnItem",
    "Coupon",
    "Promotion",
    "MarketplaceConnector",
    "Notification",
    "Report",
]



ENGINE_FILE_MAP = {
    "Store": "store",
    "SalesChannel": "sales_channel",
    "ProductListing": "product_listing",
    "ListingPrice": "listing_price",
    "ListingInventory": "listing_inventory",
    "CustomerCart": "customer_cart",
    "CartItem": "cart_item",
    "Order": "order",
    "OrderItem": "order_item",
    "Payment": "payment",
    "PaymentTransaction": "payment_transaction",
    "Shipment": "shipment",
    "ShippingTracking": "shipping_tracking",
    "ReturnRequest": "return_request",
    "ReturnItem": "return_item",
    "Coupon": "coupon",
    "Promotion": "promotion",
    "MarketplaceConnector": "marketplace_connector",
    "Notification": "notification",
    "Report": "report",
}




def _emp_fk(col: str, nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _dept_fk(col: str = "department_id", nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _customer_fk(col: str = "customer_id", nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _vendor_fk(col: str = "vendor_id", nullable: bool = True) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable={null},
        index=True,
    )'''


def _uuid_only(col: str) -> str:
    return f'''
    {col}: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)'''


def _fk(
    col: str,
    table: str,
    *,
    nullable: bool = True,
    ondelete: str = "SET NULL",
    use_alter: bool = False,
    name: str | None = None,
) -> str:
    null = "True" if nullable else "False"
    mapped = "UUID | None" if nullable else "UUID"
    extra = ""
    if use_alter:
        fk_name = name or f"fk_ec_{col}"
        extra = f',\n            use_alter=True,\n            name="{fk_name}"'
    return f'''
    {col}: Mapped[{mapped}] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "{table}",
            ondelete="{ondelete}"{extra},
        ),
        nullable={null},
        index=True,
    )'''


MODELS: dict[str, str] = {}

MODELS["store"] = f'''"""Store ORM per ERD_22 section 5.1."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcStore(Base, *EcRowMixin):
    __tablename__ = "ec_store"
    __table_args__ = (
        UniqueConstraint("company_id", "store_number", name="uk_ec_store_number"),
        UniqueConstraint("company_id", "store_code", name="uk_ec_store_code"),
        CheckConstraint(
            "store_type IN ('b2c','b2b','marketplace_brand','headless','portal')",
            name="ck_ec_store_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','inactive','retired')",
            name="ck_ec_store_status",
        ),
        Index("ix_ec_store_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    store_number: Mapped[str] = mapped_column(String(50), nullable=False)
    store_code: Mapped[str] = mapped_column(String(50), nullable=False)
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    store_type: Mapped[str] = mapped_column(String(40), nullable=False, default="b2c")
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
{_emp_fk("owner_employee_id", nullable=False)}
{_dept_fk()}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}'''

MODELS["sales_channel"] = f'''"""Sales channel ORM per ERD_22 section 5.2."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcSalesChannel(Base, *EcRowMixin):
    __tablename__ = "ec_sales_channel"
    __table_args__ = (
        UniqueConstraint("company_id", "channel_number", name="uk_ec_sales_channel_number"),
        UniqueConstraint("company_id", "channel_code", name="uk_ec_sales_channel_code"),
        CheckConstraint(
            "channel_type IN ('website','mobile_app','amazon','flipkart','shopify',"
            "'woocommerce','magento','ebay','etsy','custom_marketplace','dealer_portal',"
            "'distributor_portal')",
            name="ck_ec_sales_channel_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','paused','retired')",
            name="ck_ec_sales_channel_status",
        ),
        Index("ix_ec_sales_channel_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    channel_number: Mapped[str] = mapped_column(String(50), nullable=False)
    channel_code: Mapped[str] = mapped_column(String(50), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(255), nullable=False)
{_fk("store_id", "ecommerce.ec_store.id", nullable=False, ondelete="RESTRICT")}
    channel_type: Mapped[str] = mapped_column(String(40), nullable=False)
    external_channel_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)'''

MODELS["product_listing"] = f'''"""Product listing ORM per ERD_22 section 5.3."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcProductListing(Base, *EcRowMixin):
    __tablename__ = "ec_product_listing"
    __table_args__ = (
        UniqueConstraint("company_id", "listing_number", name="uk_ec_product_listing_number"),
        CheckConstraint(
            "status IN ('draft','submitted','approved','published','unpublished','archived')",
            name="ck_ec_product_listing_status",
        ),
        Index("ix_ec_product_listing_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    listing_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("sales_channel_id", "ecommerce.ec_sales_channel.id", nullable=False, ondelete="RESTRICT")}
{_fk("product_id", "master.master_product.id", nullable=False, ondelete="RESTRICT")}
    external_sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_listing_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    attributes_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
{_emp_fk("published_by_employee_id")}
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}'''

MODELS["listing_price"] = f'''"""Listing price ORM per ERD_22 section 5.4."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcListingPrice(Base, *EcRowMixin):
    __tablename__ = "ec_listing_price"
    __table_args__ = (
        CheckConstraint(
            "price_type IN ('retail','wholesale','contract','promotional')",
            name="ck_ec_listing_price_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','expired','superseded')",
            name="ck_ec_listing_price_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("product_listing_id", "ecommerce.ec_product_listing.id", nullable=False, ondelete="RESTRICT")}
    price_type: Mapped[str] = mapped_column(String(30), nullable=False, default="retail")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    list_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    sale_price: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(nullable=True)
{_fk("promotion_id", "ecommerce.ec_promotion.id", nullable=True, ondelete="SET NULL")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)'''

MODELS["listing_inventory"] = f'''"""Listing inventory ORM per ERD_22 section 5.5."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcListingInventory(Base, *EcRowMixin):
    __tablename__ = "ec_listing_inventory"
    __table_args__ = (
        CheckConstraint(
            "sync_status IN ('in_sync','pending','failed','stale')",
            name="ck_ec_listing_inventory_sync_status",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_ec_listing_inventory_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("product_listing_id", "ecommerce.ec_product_listing.id", nullable=False, ondelete="RESTRICT")}
{_uuid_only("warehouse_id")}
    available_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    reserved_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    safety_stock_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    last_synced_at: Mapped[datetime | None] = mapped_column(nullable=True)
{_uuid_only("inventory_item_ref_id")}
    sync_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)'''

MODELS["customer_cart"] = f'''"""Customer cart ORM per ERD_22 section 5.6."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcCustomerCart(Base, *EcRowMixin):
    __tablename__ = "ec_customer_cart"
    __table_args__ = (
        UniqueConstraint("company_id", "cart_number", name="uk_ec_customer_cart_number"),
        CheckConstraint(
            "status IN ('open','merged','converted','abandoned','cancelled')",
            name="ck_ec_customer_cart_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    cart_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("sales_channel_id", "ecommerce.ec_sales_channel.id", nullable=False, ondelete="RESTRICT")}
{_customer_fk("customer_id", nullable=False)}
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
{_fk("coupon_id", "ecommerce.ec_coupon.id", nullable=True, ondelete="SET NULL")}
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
{_fk("converted_order_id", "ecommerce.ec_order.id", nullable=True, ondelete="SET NULL", use_alter=True, name="fk_ec_customer_cart_converted_order")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)'''

MODELS["cart_item"] = f'''"""Cart item ORM per ERD_22 section 5.7."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcCartItem(Base, *EcRowMixin):
    __tablename__ = "ec_cart_item"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','removed')",
            name="ck_ec_cart_item_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("cart_id", "ecommerce.ec_customer_cart.id", nullable=False, ondelete="RESTRICT")}
{_fk("product_listing_id", "ecommerce.ec_product_listing.id", nullable=False, ondelete="RESTRICT")}
{_fk("product_id", "master.master_product.id", nullable=False, ondelete="RESTRICT")}
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)'''

MODELS["order"] = f'''"""Channel order ORM per ERD_22 section 5.8."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcOrder(Base, *EcRowMixin):
    __tablename__ = "ec_order"
    __table_args__ = (
        UniqueConstraint("company_id", "order_number", name="uk_ec_order_number"),
        CheckConstraint(
            "status IN ('new','submitted','under_review','accepted','processing','packed',"
            "'shipped','delivered','returned','cancelled','failed')",
            name="ck_ec_order_status",
        ),
        Index("ix_ec_order_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("sales_channel_id", "ecommerce.ec_sales_channel.id", nullable=False, ondelete="RESTRICT")}
{_fk("store_id", "ecommerce.ec_store.id", nullable=False, ondelete="RESTRICT")}
{_customer_fk("customer_id", nullable=False)}
{_fk("cart_id", "ecommerce.ec_customer_cart.id", nullable=True, ondelete="SET NULL")}
{_fk("coupon_id", "ecommerce.ec_coupon.id", nullable=True, ondelete="SET NULL")}
    external_order_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    shipping_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    grand_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    shipping_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    billing_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
{_uuid_only("sales_order_id")}
    placed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="new", index=True)
{WF_FIELDS}'''

MODELS["order_item"] = f'''"""Order item ORM per ERD_22 section 5.9."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcOrderItem(Base, *EcRowMixin):
    __tablename__ = "ec_order_item"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open','allocated','shipped','cancelled','returned')",
            name="ck_ec_order_item_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("order_id", "ecommerce.ec_order.id", nullable=False, ondelete="RESTRICT")}
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
{_fk("product_listing_id", "ecommerce.ec_product_listing.id", nullable=False, ondelete="RESTRICT")}
{_fk("product_id", "master.master_product.id", nullable=False, ondelete="RESTRICT")}
    external_line_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
{_uuid_only("sales_order_line_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)'''

MODELS["payment"] = f'''"""Payment ORM per ERD_22 section 5.10."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcPayment(Base, *EcRowMixin):
    __tablename__ = "ec_payment"
    __table_args__ = (
        UniqueConstraint("company_id", "payment_number", name="uk_ec_payment_number"),
        CheckConstraint(
            "payment_method IN ('card','upi','netbanking','wallet','cod','marketplace_collect','other')",
            name="ck_ec_payment_method",
        ),
        CheckConstraint(
            "status IN ('pending','authorized','captured','failed','refunded','cancelled')",
            name="ck_ec_payment_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    payment_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("order_id", "ecommerce.ec_order.id", nullable=False, ondelete="RESTRICT")}
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    gateway_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gateway_payment_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(nullable=True)
{_uuid_only("finance_journal_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)'''

MODELS["payment_transaction"] = f'''"""Payment transaction ORM per ERD_22 section 5.11."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcPaymentTransaction(Base, *EcRowMixin):
    __tablename__ = "ec_payment_transaction"
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('authorize','capture','refund','void','chargeback')",
            name="ck_ec_payment_transaction_type",
        ),
        CheckConstraint(
            "status IN ('recorded','posted','failed')",
            name="ck_ec_payment_transaction_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("payment_id", "ecommerce.ec_payment.id", nullable=False, ondelete="RESTRICT")}
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    gateway_txn_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(nullable=True)
    raw_payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
{_uuid_only("finance_journal_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)'''

MODELS["shipment"] = f'''"""Shipment ORM per ERD_22 section 5.12."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcShipment(Base, *EcRowMixin):
    __tablename__ = "ec_shipment"
    __table_args__ = (
        UniqueConstraint("company_id", "shipment_number", name="uk_ec_shipment_number"),
        CheckConstraint(
            "carrier_code IN ('shiprocket','delhivery','bluedart','fedex','dhl','other')",
            name="ck_ec_shipment_carrier",
        ),
        CheckConstraint(
            "status IN ('pending','packed','shipped','in_transit','delivered','cancelled','failed')",
            name="ck_ec_shipment_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    shipment_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("order_id", "ecommerce.ec_order.id", nullable=False, ondelete="RESTRICT")}
    carrier_code: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    tracking_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)
    shipping_label_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
{_uuid_only("sales_delivery_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)'''

MODELS["shipping_tracking"] = f'''"""Shipping tracking ORM per ERD_22 section 5.13."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcShippingTracking(Base, *EcRowMixin):
    __tablename__ = "ec_shipping_tracking"
    __table_args__ = (
        CheckConstraint(
            "tracking_status IN ('created','picked_up','in_transit','out_for_delivery',"
            "'delivered','exception','returned_to_seller')",
            name="ck_ec_shipping_tracking_status",
        ),
        CheckConstraint(
            "status IN ('recorded')",
            name="ck_ec_shipping_tracking_row_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("shipment_id", "ecommerce.ec_shipment.id", nullable=False, ondelete="RESTRICT")}
    tracked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    tracking_status: Mapped[str] = mapped_column(String(40), nullable=False)
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    carrier_event_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)'''

MODELS["return_request"] = f'''"""Return request ORM per ERD_22 section 5.14."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcReturnRequest(Base, *EcRowMixin):
    __tablename__ = "ec_return_request"
    __table_args__ = (
        UniqueConstraint("company_id", "return_number", name="uk_ec_return_request_number"),
        CheckConstraint(
            "reason_code IN ('defective','wrong_item','not_as_described','size_fit','changed_mind','other')",
            name="ck_ec_return_request_reason",
        ),
        CheckConstraint(
            "status IN ('requested','submitted','approved','rejected','pickup_scheduled',"
            "'received','inspected','refunded','closed','cancelled')",
            name="ck_ec_return_request_status",
        ),
        Index("ix_ec_return_request_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    return_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("order_id", "ecommerce.ec_order.id", nullable=False, ondelete="RESTRICT")}
{_customer_fk("customer_id", nullable=False)}
    reason_code: Mapped[str] = mapped_column(String(40), nullable=False)
    requested_at: Mapped[datetime | None] = mapped_column(nullable=True)
{_fk("refund_payment_id", "ecommerce.ec_payment.id", nullable=True, ondelete="SET NULL")}
{_uuid_only("sales_return_id")}
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="requested", index=True)
{WF_FIELDS}'''

MODELS["return_item"] = f'''"""Return item ORM per ERD_22 section 5.15."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcReturnItem(Base, *EcRowMixin):
    __tablename__ = "ec_return_item"
    __table_args__ = (
        CheckConstraint(
            "condition_code IN ('sellable','damaged','missing_parts','other')",
            name="ck_ec_return_item_condition",
        ),
        CheckConstraint(
            "status IN ('open','approved','received','refunded','rejected')",
            name="ck_ec_return_item_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("return_request_id", "ecommerce.ec_return_request.id", nullable=False, ondelete="RESTRICT")}
{_fk("order_item_id", "ecommerce.ec_order_item.id", nullable=False, ondelete="RESTRICT")}
{_fk("product_id", "master.master_product.id", nullable=False, ondelete="RESTRICT")}
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    condition_code: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    refund_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)'''

MODELS["coupon"] = f'''"""Coupon ORM per ERD_22 section 5.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcCoupon(Base, *EcRowMixin):
    __tablename__ = "ec_coupon"
    __table_args__ = (
        UniqueConstraint("company_id", "coupon_number", name="uk_ec_coupon_number"),
        UniqueConstraint("company_id", "coupon_code", name="uk_ec_coupon_code"),
        CheckConstraint(
            "discount_type IN ('percent','fixed_amount','free_shipping')",
            name="ck_ec_coupon_discount_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','exhausted','expired','cancelled')",
            name="ck_ec_coupon_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    coupon_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("store_id", "ecommerce.ec_store.id", nullable=False, ondelete="RESTRICT")}
    coupon_code: Mapped[str] = mapped_column(String(50), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(30), nullable=False)
    discount_value: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    redeemed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_from: Mapped[datetime | None] = mapped_column(nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)'''

MODELS["promotion"] = f'''"""Promotion ORM per ERD_22 section 5.17."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcPromotion(Base, *EcRowMixin):
    __tablename__ = "ec_promotion"
    __table_args__ = (
        UniqueConstraint("company_id", "promotion_number", name="uk_ec_promotion_number"),
        UniqueConstraint("company_id", "promotion_code", name="uk_ec_promotion_code"),
        CheckConstraint(
            "promotion_type IN ('percent','coupon_linked','bundle','flash_sale','seasonal')",
            name="ck_ec_promotion_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','paused','expired','cancelled')",
            name="ck_ec_promotion_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    promotion_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("store_id", "ecommerce.ec_store.id", nullable=False, ondelete="RESTRICT")}
    promotion_code: Mapped[str] = mapped_column(String(50), nullable=False)
    promotion_name: Mapped[str] = mapped_column(String(255), nullable=False)
    promotion_type: Mapped[str] = mapped_column(String(40), nullable=False)
    channel_scope_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    rules_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)'''

MODELS["marketplace_connector"] = f'''"""Marketplace connector ORM per ERD_22 section 5.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcMarketplaceConnector(Base, *EcRowMixin):
    __tablename__ = "ec_marketplace_connector"
    __table_args__ = (
        UniqueConstraint("company_id", "connector_binding_number", name="uk_ec_marketplace_connector_number"),
        CheckConstraint(
            "marketplace_code IN ('amazon','flipkart','myntra','ebay','etsy','shopify','custom')",
            name="ck_ec_marketplace_connector_code",
        ),
        CheckConstraint(
            "sync_mode IN ('realtime','scheduled','manual')",
            name="ck_ec_marketplace_connector_sync_mode",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','paused','failed','retired')",
            name="ck_ec_marketplace_connector_status",
        ),
        Index("ix_ec_marketplace_connector_tenant_co_status", "tenant_id", "company_id", "status"),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    connector_binding_number: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("sales_channel_id", "ecommerce.ec_sales_channel.id", nullable=False, ondelete="RESTRICT")}
    marketplace_code: Mapped[str] = mapped_column(String(40), nullable=False)
{_uuid_only("int_external_system_id")}
{_uuid_only("int_connector_id")}
{_vendor_fk("vendor_id")}
    sync_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled")
    last_sync_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}'''

MODELS["notification"] = f'''"""Notification ORM per ERD_22 section 5.19."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcNotification(Base, *EcRowMixin):
    __tablename__ = "ec_notification"
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('order_received','order_shipped','order_delivered',"
            "'return_requested','inventory_low','sync_failed','payment_failed','other')",
            name="ck_ec_notification_type",
        ),
        CheckConstraint(
            "channel IN ('email','sms','whatsapp','push','in_app')",
            name="ck_ec_notification_channel",
        ),
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_ec_notification_delivery_status",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_ec_notification_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
{_fk("sales_channel_id", "ecommerce.ec_sales_channel.id", nullable=True, ondelete="SET NULL")}
{_fk("order_id", "ecommerce.ec_order.id", nullable=True, ondelete="SET NULL")}
{_fk("return_request_id", "ecommerce.ec_return_request.id", nullable=True, ondelete="SET NULL")}
{_fk("shipment_id", "ecommerce.ec_shipment.id", nullable=True, ondelete="SET NULL")}
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=False, default="email")
{_customer_fk("recipient_customer_id")}
{_emp_fk("recipient_employee_id")}
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)'''

MODELS["report"] = f'''"""Report ORM per ERD_22 section 5.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcReport(Base, *EcRowMixin):
    __tablename__ = "ec_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_ec_report_code"),
        CheckConstraint(
            "report_type IN ('channel_revenue','orders','conversion','returns',"
            "'listing_sync','inventory_sync','promotion_performance')",
            name="ck_ec_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_ec_report_status",
        ),
        {{"schema": "ecommerce"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    report_code: Mapped[str] = mapped_column(String(50), nullable=False)
{_fk("store_id", "ecommerce.ec_store.id", nullable=True, ondelete="SET NULL")}
{_fk("sales_channel_id", "ecommerce.ec_sales_channel.id", nullable=True, ondelete="SET NULL")}
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)'''


# Engine bodies continued in part 2 — written by gen via ENGINE_BODIES below
ENGINE_BODIES: dict[str, str] = {
    "Store": """
class StoreEngine:
    def submit(self, row) -> None:
        if row.status != StoreStatus.DRAFT.value:
            raise InvalidStoreState("Only draft stores can be submitted")
        row.status = StoreStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != StoreStatus.SUBMITTED.value:
            raise InvalidStoreState("Only submitted stores can be approved")
        row.status = StoreStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = StoreStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = StoreStatus.INACTIVE.value

    def retire(self, row) -> None:
        row.status = StoreStatus.RETIRED.value
""",
    "SalesChannel": """
class SalesChannelEngine:
    def activate(self, row) -> None:
        row.status = SalesChannelStatus.ACTIVE.value
        row.is_active = True

    def pause(self, row) -> None:
        row.status = SalesChannelStatus.PAUSED.value
        row.is_active = False

    def retire(self, row) -> None:
        row.status = SalesChannelStatus.RETIRED.value
        row.is_active = False
""",
    "ProductListing": """
class ProductListingEngine:
    def submit(self, row) -> None:
        if row.status != ProductListingStatus.DRAFT.value:
            raise InvalidProductListingState("Only draft listings can be submitted")
        row.status = ProductListingStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProductListingStatus.SUBMITTED.value:
            raise InvalidProductListingState("Only submitted listings can be approved")
        row.status = ProductListingStatus.APPROVED.value

    def publish(self, row) -> None:
        if row.status not in {ProductListingStatus.APPROVED.value, ProductListingStatus.UNPUBLISHED.value}:
            raise InvalidProductListingState("Only approved listings can be published")
        row.status = ProductListingStatus.PUBLISHED.value

    def unpublish(self, row) -> None:
        row.status = ProductListingStatus.UNPUBLISHED.value

    def archive(self, row) -> None:
        row.status = ProductListingStatus.ARCHIVED.value
""",
    "ListingPrice": """
class ListingPriceEngine:
    def activate(self, row) -> None:
        row.status = ListingPriceStatus.ACTIVE.value

    def expire(self, row) -> None:
        row.status = ListingPriceStatus.EXPIRED.value

    def supersede(self, row) -> None:
        row.status = ListingPriceStatus.SUPERSEDED.value
""",
    "ListingInventory": """
class ListingInventoryEngine:
    def activate(self, row) -> None:
        row.status = ListingInventoryStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ListingInventoryStatus.INACTIVE.value
""",
    "CustomerCart": """
class CustomerCartEngine:
    def convert(self, row) -> None:
        row.status = CustomerCartStatus.CONVERTED.value

    def abandon(self, row) -> None:
        row.status = CustomerCartStatus.ABANDONED.value

    def cancel(self, row) -> None:
        row.status = CustomerCartStatus.CANCELLED.value
""",
    "CartItem": """
class CartItemEngine:
    def remove(self, row) -> None:
        row.status = CartItemStatus.REMOVED.value
""",
    "Order": """
class OrderEngine:
    def submit(self, row) -> None:
        if row.status != OrderStatus.NEW.value:
            raise InvalidOrderState("Only new orders can be submitted")
        row.status = OrderStatus.SUBMITTED.value

    def accept(self, row) -> None:
        if row.status not in {OrderStatus.SUBMITTED.value, OrderStatus.UNDER_REVIEW.value}:
            raise InvalidOrderState("Order not reviewable for acceptance")
        row.status = OrderStatus.ACCEPTED.value

    def cancel(self, row) -> None:
        row.status = OrderStatus.CANCELLED.value
""",
    "OrderItem": """
class OrderItemEngine:
    def allocate(self, row) -> None:
        row.status = OrderItemStatus.ALLOCATED.value

    def ship(self, row) -> None:
        row.status = OrderItemStatus.SHIPPED.value

    def cancel(self, row) -> None:
        row.status = OrderItemStatus.CANCELLED.value
""",
    "Payment": """
class PaymentEngine:
    def authorize(self, row) -> None:
        row.status = PaymentStatus.AUTHORIZED.value

    def capture(self, row) -> None:
        row.status = PaymentStatus.CAPTURED.value

    def fail(self, row) -> None:
        row.status = PaymentStatus.FAILED.value

    def refund(self, row) -> None:
        row.status = PaymentStatus.REFUNDED.value
""",
    "PaymentTransaction": """
class PaymentTransactionEngine:
    def post(self, row) -> None:
        row.status = PaymentTransactionStatus.POSTED.value

    def fail(self, row) -> None:
        row.status = PaymentTransactionStatus.FAILED.value
""",
    "Shipment": """
class ShipmentEngine:
    def pack(self, row) -> None:
        row.status = ShipmentStatus.PACKED.value

    def ship(self, row) -> None:
        row.status = ShipmentStatus.SHIPPED.value

    def deliver(self, row) -> None:
        row.status = ShipmentStatus.DELIVERED.value

    def cancel(self, row) -> None:
        row.status = ShipmentStatus.CANCELLED.value
""",
    "ShippingTracking": """
class ShippingTrackingEngine:
    def record(self, row) -> None:
        row.status = ShippingTrackingStatus.RECORDED.value
""",
    "ReturnRequest": """
class ReturnRequestEngine:
    def submit(self, row) -> None:
        if row.status != ReturnRequestStatus.REQUESTED.value:
            raise InvalidReturnRequestState("Only requested returns can be submitted")
        row.status = ReturnRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ReturnRequestStatus.SUBMITTED.value:
            raise InvalidReturnRequestState("Only submitted returns can be approved")
        row.status = ReturnRequestStatus.APPROVED.value

    def reject(self, row) -> None:
        row.status = ReturnRequestStatus.REJECTED.value

    def close(self, row) -> None:
        row.status = ReturnRequestStatus.CLOSED.value
""",
    "ReturnItem": """
class ReturnItemEngine:
    def approve(self, row) -> None:
        row.status = ReturnItemStatus.APPROVED.value

    def receive(self, row) -> None:
        row.status = ReturnItemStatus.RECEIVED.value

    def refund(self, row) -> None:
        row.status = ReturnItemStatus.REFUNDED.value
""",
    "Coupon": """
class CouponEngine:
    def activate(self, row) -> None:
        row.status = CouponStatus.ACTIVE.value

    def exhaust(self, row) -> None:
        row.status = CouponStatus.EXHAUSTED.value

    def expire(self, row) -> None:
        row.status = CouponStatus.EXPIRED.value
""",
    "Promotion": """
class PromotionEngine:
    def activate(self, row) -> None:
        row.status = PromotionStatus.ACTIVE.value

    def pause(self, row) -> None:
        row.status = PromotionStatus.PAUSED.value

    def expire(self, row) -> None:
        row.status = PromotionStatus.EXPIRED.value
""",
    "MarketplaceConnector": """
class MarketplaceConnectorEngine:
    def submit(self, row) -> None:
        if row.status != MarketplaceConnectorStatus.DRAFT.value:
            raise InvalidMarketplaceConnectorState("Only draft connectors can be submitted")
        row.status = MarketplaceConnectorStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != MarketplaceConnectorStatus.SUBMITTED.value:
            raise InvalidMarketplaceConnectorState("Only submitted connectors can be approved")
        row.status = MarketplaceConnectorStatus.APPROVED.value

    def sync(self, row) -> None:
        row.status = MarketplaceConnectorStatus.ACTIVE.value

    def pause(self, row) -> None:
        row.status = MarketplaceConnectorStatus.PAUSED.value

    def mark_failed(self, row) -> None:
        row.status = MarketplaceConnectorStatus.FAILED.value
""",
    "Notification": """
class NotificationEngine:
    def acknowledge(self, row) -> None:
        row.delivery_status = "read"
        row.status = NotificationStatus.ARCHIVED.value
""",
    "Report": """
class ReportEngine:
    def finalize(self, row) -> None:
        row.status = ReportStatus.FINALIZED.value
""",
}




def gen_scaffold() -> None:
    w(ECOMMERCE / "__init__.py", '"""E-Commerce / External Channel module — Sprint 22."""\n')
    w(ECOMMERCE / "domain" / "__init__.py", '"""E-Commerce domain layer."""\n')
    w(ECOMMERCE / "adapters" / "__init__.py", '"""E-Commerce cross-module adapters."""\n')
    w(ECOMMERCE / "service" / "__init__.py", '"""E-Commerce services — populated after generation."""\n')
    w(ECOMMERCE / "service" / "engines" / "__init__.py", '"""E-Commerce engines — populated after generation."""\n')
    w(ECOMMERCE / "repository" / "__init__.py", '"""E-Commerce repositories."""\n')
    w(ECOMMERCE / "models" / "__init__.py", '"""E-Commerce models — populated after generation."""\n')
    w(
        ECOMMERCE / "models" / "mixins.py",
        '''"""E-Commerce ORM mixin bundles per ERD_22."""

from database.mixins import (
    AuditMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

EcRowMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
    )


def gen_domain() -> None:
    w(
        ECOMMERCE / "domain" / "enums.py",
        '''"""E-Commerce domain enums per ERD_22 section 8."""

from enum import Enum


class StoreStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class SalesChannelStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class ProductListingStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"
    ARCHIVED = "archived"


class ListingPriceStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class ListingInventoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ListingInventorySyncStatus(str, Enum):
    IN_SYNC = "in_sync"
    PENDING = "pending"
    FAILED = "failed"
    STALE = "stale"


class CustomerCartStatus(str, Enum):
    OPEN = "open"
    MERGED = "merged"
    CONVERTED = "converted"
    ABANDONED = "abandoned"
    CANCELLED = "cancelled"


class CartItemStatus(str, Enum):
    ACTIVE = "active"
    REMOVED = "removed"


class OrderStatus(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderItemStatus(str, Enum):
    OPEN = "open"
    ALLOCATED = "allocated"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentTransactionStatus(str, Enum):
    RECORDED = "recorded"
    POSTED = "posted"
    FAILED = "failed"


class ShipmentStatus(str, Enum):
    PENDING = "pending"
    PACKED = "packed"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ShippingTrackingStatus(str, Enum):
    RECORDED = "recorded"


class ReturnRequestStatus(str, Enum):
    REQUESTED = "requested"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PICKUP_SCHEDULED = "pickup_scheduled"
    RECEIVED = "received"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ReturnItemStatus(str, Enum):
    OPEN = "open"
    APPROVED = "approved"
    RECEIVED = "received"
    REFUNDED = "refunded"
    REJECTED = "rejected"


class CouponStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXHAUSTED = "exhausted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PromotionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class MarketplaceConnectorStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"
    RETIRED = "retired"


class NotificationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class EcommerceEntityType(str, Enum):
    STORE = "store"
    SALES_CHANNEL = "sales_channel"
    PRODUCT_LISTING = "product_listing"
    CUSTOMER_CART = "customer_cart"
    ORDER = "order"
    PAYMENT = "payment"
    SHIPMENT = "shipment"
    RETURN_REQUEST = "return_request"
    COUPON = "coupon"
    PROMOTION = "promotion"
    MARKETPLACE_CONNECTOR = "marketplace_connector"

CODE_PREFIXES: dict[EcommerceEntityType, tuple[str, int, bool]] = {
    EcommerceEntityType.STORE: ("STO-", 6, True),
    EcommerceEntityType.SALES_CHANNEL: ("CHN-", 6, True),
    EcommerceEntityType.PRODUCT_LISTING: ("LST-", 6, True),
    EcommerceEntityType.CUSTOMER_CART: ("CRT-", 6, True),
    EcommerceEntityType.ORDER: ("ECO-", 6, True),
    EcommerceEntityType.PAYMENT: ("PAY-", 6, True),
    EcommerceEntityType.SHIPMENT: ("SHP-", 6, True),
    EcommerceEntityType.RETURN_REQUEST: ("RET-", 6, True),
    EcommerceEntityType.COUPON: ("CPN-", 6, True),
    EcommerceEntityType.PROMOTION: ("PRO-", 6, True),
    EcommerceEntityType.MARKETPLACE_CONNECTOR: ("MPK-", 6, True),
}
''',
    )
    exc_lines = []
    for _, _, name, _ in TABLES:
        exc_lines.append(
            f'''
class Invalid{name}State(ConflictException):
    def __init__(self, message: str = "Invalid {name.lower()} state") -> None:
        super().__init__(message)
'''
        )
    w(
        ECOMMERCE / "domain" / "exceptions.py",
        '"""E-Commerce domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )
    w(
        ECOMMERCE / "domain" / "value_objects.py",
        '''"""E-Commerce value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EcommerceCodes:
    document_number: str
''',
    )
    w(
        ECOMMERCE / "domain" / "entities.py",
        '''"""E-Commerce domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class StoreIdentity:
    store_id: UUID
    store_number: str
''',
    )


def gen_models() -> None:
    for key, body in MODELS.items():
        w(ECOMMERCE / "models" / f"{key}.py", body)
    imports = "\n".join(
        f"from modules.ecommerce.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP
    )
    all_names = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        ECOMMERCE / "models" / "__init__.py",
        f'"""E-Commerce ORM models."""\n\n{imports}\n\n__all__ = [\n    {all_names},\n]\n',
    )


def gen_migrations() -> None:
    w(
        ALEMBIC / "0399_create_ecommerce_schema.py",
        '''"""Create ecommerce schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0399_create_ecommerce_schema"
down_revision: str | None = "0398_seed_integration_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS ecommerce")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS ecommerce CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.ecommerce.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
                for m in target
            )
            creates = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.create(bind=op.get_bind(), checkfirst=True)"
                for m in target
            )
            drops = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.drop(bind=op.get_bind(), checkfirst=True)"
                for m in reversed(target)
            )
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create ec_shipment and ec_shipping_tracking tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

{imports}

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {creates}


def downgrade() -> None:
    {drops}
''',
            )
        else:
            cls = CLASS_MAP[target]
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.{target} import {cls}  # noqa: F401

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {cls}.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    {cls}.__table__.drop(bind=op.get_bind(), checkfirst=True)
''',
            )


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    return f'''"""E-Commerce {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.ecommerce.models import {cls}
from modules.ecommerce.repository.base import EcommerceScopedRepository, utcnow


class {name}Repository(EcommerceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_ecommerce_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_ecommerce_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> {cls}:
        row = {cls}(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> {cls} | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
'''


def gen_repos() -> None:
    w(
        ECOMMERCE / "repository" / "base.py",
        '''"""E-Commerce scoped repository base."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EcommerceScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_ecommerce_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = EcommerceScopedRepository.apply_tenant_filter(stmt, model, ctx)
        if ctx.company_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(model.company_id == ctx.company_id)
        if (
            branch_scoped
            and ctx.branch_id
            and ctx.user_type not in {"super_admin", "tenant_admin"}
            and hasattr(model, "branch_id")
        ):
            stmt = stmt.where(model.branch_id == ctx.branch_id)
        return stmt

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            EcommerceScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        ECOMMERCE / "repository" / "code_sequence_repository.py",
        '''"""E-Commerce code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.ecommerce.domain.enums import CODE_PREFIXES, EcommerceEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: EcommerceEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width, include_year = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-" if include_year else prefix
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
            model.is_deleted.is_(False),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{full_prefix}{seq:0{width}d}"
''',
    )
    for module, cls, name, branch in TABLES:
        w(
            ECOMMERCE / "repository" / f"{module}_repository.py",
            repo_template(module, cls, name, branch),
        )


def gen_engines() -> None:
    status_imports = {n: f"{n}Status" for n in ENGINE_NAMES}
    exc_imports = {
        "Store": "InvalidStoreState",
        "ProductListing": "InvalidProductListingState",
        "Order": "InvalidOrderState",
        "ReturnRequest": "InvalidReturnRequestState",
        "MarketplaceConnector": "InvalidMarketplaceConnectorState",
    }
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        st = status_imports[eng_name]
        header = f'"""{eng_name} lifecycle engine."""\n\n'
        header += f"from modules.ecommerce.domain.enums import (\n    {st},\n)\n"
        if eng_name in exc_imports:
            header += (
                f"from modules.ecommerce.domain.exceptions import (\n"
                f"    {exc_imports[eng_name]},\n)\n"
            )
        header += "\n"
        w(ECOMMERCE / "service" / "engines" / f"{fname}_engine.py", header + body.lstrip("\n"))
    lines = [
        f"from modules.ecommerce.service.engines.{ENGINE_FILE_MAP[n]}_engine "
        f"import {n}Engine"
        for n in ENGINE_NAMES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_NAMES)
    w(
        ECOMMERCE / "service" / "engines" / "__init__.py",
        '"""E-Commerce business engines."""\n\n'
        + "\n".join(lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def catalog_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    engine_name: str,
) -> str:
    return f'''"""{svc_name} application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.ecommerce.models import {cls}
from modules.ecommerce.repository.{entity}_repository import {repo_name}Repository
from modules.ecommerce.service.engines import {engine_name}Engine
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = EcommerceScopeValidator(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        row = self._repo.create(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ec_{entity}",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
'''


def numbered_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    entity_type: str,
    code_col: str,
    engine_name: str,
    actions: list[str],
) -> str:
    action_methods = ""
    for act in actions:
        action_methods += f'''
    def {act}(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.{act}(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''
    return f'''"""{svc_name}."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.models import {cls}
from modules.ecommerce.repository.{entity}_repository import {repo_name}Repository
from modules.ecommerce.service.engines import {engine_name}Engine
from modules.ecommerce.service.ecommerce_number_service import EcommerceNumberService
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = EcommerceScopeValidator(db)
        self._numbers = EcommerceNumberService(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(EcommerceEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, {code_col}=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
{action_methods}
'''


def gen_services() -> None:
    w(
        ECOMMERCE / "service" / "ecommerce_scope_validator.py",
        '''"""E-Commerce scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.ecommerce.repository.base import EcommerceScopedRepository


class EcommerceScopeValidator(EcommerceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        ECOMMERCE / "service" / "ecommerce_number_service.py",
        '''"""E-Commerce numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.repository.code_sequence_repository import CodeSequenceRepository


class EcommerceNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: EcommerceEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    simple_specs = [
        ("ListingPriceService", "EcListingPrice", "ListingPrice", "listing_price", "ListingPrice", "listing_price_service.py"),
        ("ListingInventoryService", "EcListingInventory", "ListingInventory", "listing_inventory", "ListingInventory", "listing_inventory_service.py"),
        ("CartItemService", "EcCartItem", "CartItem", "cart_item", "CartItem", "cart_item_service.py"),
        ("OrderItemService", "EcOrderItem", "OrderItem", "order_item", "OrderItem", "order_item_service.py"),
        ("PaymentTransactionService", "EcPaymentTransaction", "PaymentTransaction", "payment_transaction", "PaymentTransaction", "payment_transaction_service.py"),
        ("ShippingTrackingService", "EcShippingTracking", "ShippingTracking", "shipping_tracking", "ShippingTracking", "shipping_tracking_service.py"),
        ("ReturnItemService", "EcReturnItem", "ReturnItem", "return_item", "ReturnItem", "return_item_service.py"),
        ("SalesChannelService", "EcSalesChannel", "SalesChannel", "sales_channel", "SalesChannel", "sales_channel_service.py"),
        ("NotificationService", "EcNotification", "Notification", "notification", "Notification", "notification_service.py"),
        ("ReportService", "EcReport", "Report", "report", "Report", "report_service.py"),
    ]

    for svc, cls, repo, entity, eng, fname in simple_specs:
        body = catalog_service(svc, cls, repo, entity, eng)
        if svc == "NotificationService":
            body = body.rstrip() + '''

    def acknowledge(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.acknowledge(row)
        return self._repo.update(ctx, row_id, delivery_status=row.delivery_status)
'''
        w(ECOMMERCE / "service" / fname, body)

    numbered = [
        ("StoreService", "EcStore", "Store", "store", "STORE", "store_number", "Store", ["submit", "approve"], "store_service.py"),
        ("ProductListingService", "EcProductListing", "ProductListing", "product_listing", "PRODUCT_LISTING", "listing_number", "ProductListing", ["submit", "approve", "publish"], "product_listing_service.py"),
        ("CustomerCartService", "EcCustomerCart", "CustomerCart", "customer_cart", "CUSTOMER_CART", "cart_number", "CustomerCart", [], "customer_cart_service.py"),
        ("OrderService", "EcOrder", "Order", "order", "ORDER", "order_number", "Order", ["submit", "accept", "cancel"], "order_service.py"),
        ("PaymentService", "EcPayment", "Payment", "payment", "PAYMENT", "payment_number", "Payment", ["capture", "refund"], "payment_service.py"),
        ("ShipmentService", "EcShipment", "Shipment", "shipment", "SHIPMENT", "shipment_number", "Shipment", [], "shipment_service.py"),
        ("ReturnRequestService", "EcReturnRequest", "ReturnRequest", "return_request", "RETURN_REQUEST", "return_number", "ReturnRequest", ["submit", "approve", "reject"], "return_request_service.py"),
        ("CouponService", "EcCoupon", "Coupon", "coupon", "COUPON", "coupon_number", "Coupon", [], "coupon_service.py"),
        ("PromotionService", "EcPromotion", "Promotion", "promotion", "PROMOTION", "promotion_number", "Promotion", [], "promotion_service.py"),
        ("MarketplaceConnectorService", "EcMarketplaceConnector", "MarketplaceConnector", "marketplace_connector", "MARKETPLACE_CONNECTOR", "connector_binding_number", "MarketplaceConnector", ["submit", "approve", "sync"], "marketplace_connector_service.py"),
    ]

    for svc, cls, repo, entity, etype, col, eng, acts, fname in numbered:
        w(
            ECOMMERCE / "service" / fname,
            numbered_service(svc, cls, repo, entity, etype, col, eng, acts),
        )

    w(
ECOMMERCE / "service" / "ecommerce_integration_service.py",
        '''"""E-Commerce integration service using peer adapters (C-01 + UUID refs)."""

from uuid import UUID

from decimal import Decimal

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.ecommerce.adapters.finance_port import EcommerceFinanceAdapter
from modules.ecommerce.adapters.integration_hub_port import EcommerceIntegrationHubAdapter
from modules.ecommerce.adapters.inventory_port import EcommerceInventoryAdapter
from modules.ecommerce.adapters.master_data_port import EcommerceMasterDataAdapter
from modules.ecommerce.adapters.organization_port import EcommerceOrganizationAdapter
from modules.ecommerce.adapters.sales_port import EcommerceSalesAdapter
from modules.ecommerce.models import EcPayment


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
''',
    )

    svc_imports = """from modules.ecommerce.service.cart_item_service import CartItemService
from modules.ecommerce.service.coupon_service import CouponService
from modules.ecommerce.service.customer_cart_service import CustomerCartService
from modules.ecommerce.service.ecommerce_integration_service import EcommerceIntegrationService
from modules.ecommerce.service.listing_inventory_service import ListingInventoryService
from modules.ecommerce.service.listing_price_service import ListingPriceService
from modules.ecommerce.service.marketplace_connector_service import MarketplaceConnectorService
from modules.ecommerce.service.notification_service import NotificationService
from modules.ecommerce.service.order_item_service import OrderItemService
from modules.ecommerce.service.order_service import OrderService
from modules.ecommerce.service.payment_service import PaymentService
from modules.ecommerce.service.payment_transaction_service import PaymentTransactionService
from modules.ecommerce.service.product_listing_service import ProductListingService
from modules.ecommerce.service.promotion_service import PromotionService
from modules.ecommerce.service.report_service import ReportService
from modules.ecommerce.service.return_item_service import ReturnItemService
from modules.ecommerce.service.return_request_service import ReturnRequestService
from modules.ecommerce.service.sales_channel_service import SalesChannelService
from modules.ecommerce.service.shipment_service import ShipmentService
from modules.ecommerce.service.shipping_tracking_service import ShippingTrackingService
from modules.ecommerce.service.store_service import StoreService"""

    w(
        ECOMMERCE / "service" / "application_service.py",
        f'''"""E-Commerce application service facade."""

from sqlalchemy.orm import Session

{svc_imports}


class EcommerceApplicationService:
    def __init__(self, db: Session) -> None:
        self.stores = StoreService(db)
        self.sales_channels = SalesChannelService(db)
        self.product_listings = ProductListingService(db)
        self.listing_prices = ListingPriceService(db)
        self.listing_inventories = ListingInventoryService(db)
        self.customer_carts = CustomerCartService(db)
        self.cart_items = CartItemService(db)
        self.orders = OrderService(db)
        self.order_items = OrderItemService(db)
        self.payments = PaymentService(db)
        self.payment_transactions = PaymentTransactionService(db)
        self.shipments = ShipmentService(db)
        self.shipping_trackings = ShippingTrackingService(db)
        self.return_requests = ReturnRequestService(db)
        self.return_items = ReturnItemService(db)
        self.coupons = CouponService(db)
        self.promotions = PromotionService(db)
        self.marketplace_connectors = MarketplaceConnectorService(db)
        self.notifications = NotificationService(db)
        self.reports = ReportService(db)
        self.integration = EcommerceIntegrationService(db)
''',
    )

    w(
        ECOMMERCE / "service" / "__init__.py",
        f'''"""E-Commerce services."""

from modules.ecommerce.service.application_service import EcommerceApplicationService
{svc_imports}

__all__ = [
    "CartItemService",
    "CouponService",
    "CustomerCartService",
    "EcommerceApplicationService",
    "EcommerceIntegrationService",
    "ListingInventoryService",
    "ListingPriceService",
    "MarketplaceConnectorService",
    "NotificationService",
    "OrderItemService",
    "OrderService",
    "PaymentService",
    "PaymentTransactionService",
    "ProductListingService",
    "PromotionService",
    "ReportService",
    "ReturnItemService",
    "ReturnRequestService",
    "SalesChannelService",
    "ShipmentService",
    "ShippingTrackingService",
    "StoreService",
]
''',
    )


def gen_adapters() -> None:
    w(
        ECOMMERCE / "adapters" / "master_data_port.py",
        '''"""Master Data port — employee / customer / product / vendor (C-01)."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.customer_service import CustomerService
from modules.master_data.service.employee_service import EmployeeService
from modules.master_data.service.product_service import ProductService
from modules.master_data.service.vendor_service import VendorService


class EcommerceMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._customers = CustomerService(db)
        self._employees = EmployeeService(db)
        self._products = ProductService(db)
        self._vendors = VendorService(db)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._customers.get_customer(ctx, customer_id)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._products.get_product(ctx, product_id)

    def get_vendor(self, ctx: TenantContext, vendor_id: UUID):
        return self._vendors.get_vendor(ctx, vendor_id)
''',
    )
    w(
        ECOMMERCE / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class EcommerceOrganizationAdapter:
    def __init__(self, db: Session) -> None:
        self._departments = DepartmentRepository(db)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        row = self._departments.get_by_id(ctx, department_id)
        if row is None:
            raise NotFoundException("Department not found")
        return row
''',
    )
    w(
        ECOMMERCE / "adapters" / "finance_port.py",
        '''"""Finance port — PostingService.post_system_journal only; store finance_journal_id."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import JournalType
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext
from modules.ecommerce.models import EcPayment


class EcommerceFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._journals = JournalService(db)
        self._posting = PostingService(db)

    def post_payment_capture(
        self,
        ctx: TenantContext,
        row: EcPayment,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_journal(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            document_label=f"Payment {row.payment_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )

    def post_payment_refund(
        self,
        ctx: TenantContext,
        row: EcPayment,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_journal(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            document_label=f"Refund {row.payment_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )

    def _post_journal(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID | None,
        document_label: str,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None,
    ) -> UUID:
        amount = amount.quantize(Decimal("0.0001"))
        resolved_branch_id = branch_id if branch_id is not None else ctx.branch_id
        if resolved_branch_id is None:
            msg = "branch_id is required for E-Commerce finance posting"
            raise ValueError(msg)
        journal = self._journals.create_journal(
            ctx,
            company_id=company_id,
            branch_id=resolved_branch_id,
            journal_date=date.today(),
            description=f"E-Commerce {document_label}",
            journal_type=JournalType.SYSTEM.value,
            fiscal_year_id=fiscal_year_id,
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=1,
            account_id=debit_account_id,
            debit_amount=float(amount),
            credit_amount=0,
            description="E-Commerce debit",
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=2,
            account_id=credit_account_id,
            debit_amount=0,
            credit_amount=float(amount),
            description="E-Commerce credit",
        )
        self._posting.post_system_journal(ctx, journal.id)
        return journal.id
''',
    )
    w(
        ECOMMERCE / "adapters" / "sales_port.py",
        '''"""Sales port — order-of-record via service; UUID refs only."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext


class EcommerceSalesAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def resolve_sales_order_ref(self, ctx: TenantContext, sales_order_id: UUID | None) -> UUID | None:
        _ = (ctx, self._db)
        return sales_order_id
''',
    )
    w(
        ECOMMERCE / "adapters" / "inventory_port.py",
        '''"""Inventory port — stock authority via services/events; UUID refs only."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext


class EcommerceInventoryAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def resolve_inventory_item_ref(
        self, ctx: TenantContext, inventory_item_ref_id: UUID | None
    ) -> UUID | None:
        _ = (ctx, self._db)
        return inventory_item_ref_id
''',
    )
    w(
        ECOMMERCE / "adapters" / "integration_hub_port.py",
        '''"""Integration Hub port — connector/system UUID refs only."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext


class EcommerceIntegrationHubAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def resolve_connector_ref(self, ctx: TenantContext, int_connector_id: UUID | None) -> UUID | None:
        _ = (ctx, self._db)
        return int_connector_id

    def resolve_external_system_ref(
        self, ctx: TenantContext, int_external_system_id: UUID | None
    ) -> UUID | None:
        _ = (ctx, self._db)
        return int_external_system_id
''',
    )
    w(
        ECOMMERCE / "adapters" / "__init__.py",
        '"""E-Commerce peer adapters."""\n',
    )



def gen_permissions() -> None:
    w(
        ECOMMERCE / "permissions.py",
        '''"""E-Commerce permission constants per ERD_22 section 10."""

ECOMMERCE_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("ecommerce.store:read", "ecommerce.store", "read", "ecommerce"),
    ("ecommerce.store:create", "ecommerce.store", "create", "ecommerce"),
    ("ecommerce.store:update", "ecommerce.store", "update", "ecommerce"),
    ("ecommerce.store:submit", "ecommerce.store", "submit", "ecommerce"),
    ("ecommerce.store:approve", "ecommerce.store", "approve", "ecommerce"),
    ("ecommerce.channel:read", "ecommerce.channel", "read", "ecommerce"),
    ("ecommerce.channel:create", "ecommerce.channel", "create", "ecommerce"),
    ("ecommerce.channel:update", "ecommerce.channel", "update", "ecommerce"),
    ("ecommerce.channel:submit", "ecommerce.channel", "submit", "ecommerce"),
    ("ecommerce.channel:approve", "ecommerce.channel", "approve", "ecommerce"),
    ("ecommerce.listing:read", "ecommerce.listing", "read", "ecommerce"),
    ("ecommerce.listing:create", "ecommerce.listing", "create", "ecommerce"),
    ("ecommerce.listing:update", "ecommerce.listing", "update", "ecommerce"),
    ("ecommerce.listing:submit", "ecommerce.listing", "submit", "ecommerce"),
    ("ecommerce.listing:approve", "ecommerce.listing", "approve", "ecommerce"),
    ("ecommerce.listing:publish", "ecommerce.listing", "publish", "ecommerce"),
    ("ecommerce.price:read", "ecommerce.price", "read", "ecommerce"),
    ("ecommerce.price:create", "ecommerce.price", "create", "ecommerce"),
    ("ecommerce.price:update", "ecommerce.price", "update", "ecommerce"),
    ("ecommerce.price:submit", "ecommerce.price", "submit", "ecommerce"),
    ("ecommerce.price:approve", "ecommerce.price", "approve", "ecommerce"),
    ("ecommerce.price:publish", "ecommerce.price", "publish", "ecommerce"),
    ("ecommerce.listing_inventory:read", "ecommerce.listing_inventory", "read", "ecommerce"),
    ("ecommerce.listing_inventory:create", "ecommerce.listing_inventory", "create", "ecommerce"),
    ("ecommerce.listing_inventory:update", "ecommerce.listing_inventory", "update", "ecommerce"),
    ("ecommerce.listing_inventory:submit", "ecommerce.listing_inventory", "submit", "ecommerce"),
    ("ecommerce.listing_inventory:approve", "ecommerce.listing_inventory", "approve", "ecommerce"),
    ("ecommerce.listing_inventory:publish", "ecommerce.listing_inventory", "publish", "ecommerce"),
    ("ecommerce.cart:read", "ecommerce.cart", "read", "ecommerce"),
    ("ecommerce.cart:create", "ecommerce.cart", "create", "ecommerce"),
    ("ecommerce.cart:update", "ecommerce.cart", "update", "ecommerce"),
    ("ecommerce.order:read", "ecommerce.order", "read", "ecommerce"),
    ("ecommerce.order:create", "ecommerce.order", "create", "ecommerce"),
    ("ecommerce.order:update", "ecommerce.order", "update", "ecommerce"),
    ("ecommerce.order:submit", "ecommerce.order", "submit", "ecommerce"),
    ("ecommerce.order:review", "ecommerce.order", "review", "ecommerce"),
    ("ecommerce.order:accept", "ecommerce.order", "accept", "ecommerce"),
    ("ecommerce.order:cancel", "ecommerce.order", "cancel", "ecommerce"),
    ("ecommerce.payment:read", "ecommerce.payment", "read", "ecommerce"),
    ("ecommerce.payment:create", "ecommerce.payment", "create", "ecommerce"),
    ("ecommerce.payment:capture", "ecommerce.payment", "capture", "ecommerce"),
    ("ecommerce.payment:refund", "ecommerce.payment", "refund", "ecommerce"),
    ("ecommerce.payment_txn:read", "ecommerce.payment_txn", "read", "ecommerce"),
    ("ecommerce.payment_txn:create", "ecommerce.payment_txn", "create", "ecommerce"),
    ("ecommerce.payment_txn:capture", "ecommerce.payment_txn", "capture", "ecommerce"),
    ("ecommerce.payment_txn:refund", "ecommerce.payment_txn", "refund", "ecommerce"),
    ("ecommerce.shipment:read", "ecommerce.shipment", "read", "ecommerce"),
    ("ecommerce.shipment:create", "ecommerce.shipment", "create", "ecommerce"),
    ("ecommerce.shipment:update", "ecommerce.shipment", "update", "ecommerce"),
    ("ecommerce.tracking:read", "ecommerce.tracking", "read", "ecommerce"),
    ("ecommerce.tracking:create", "ecommerce.tracking", "create", "ecommerce"),
    ("ecommerce.tracking:update", "ecommerce.tracking", "update", "ecommerce"),
    ("ecommerce.return:read", "ecommerce.return", "read", "ecommerce"),
    ("ecommerce.return:create", "ecommerce.return", "create", "ecommerce"),
    ("ecommerce.return:submit", "ecommerce.return", "submit", "ecommerce"),
    ("ecommerce.return:approve", "ecommerce.return", "approve", "ecommerce"),
    ("ecommerce.return:reject", "ecommerce.return", "reject", "ecommerce"),
    ("ecommerce.coupon:read", "ecommerce.coupon", "read", "ecommerce"),
    ("ecommerce.coupon:create", "ecommerce.coupon", "create", "ecommerce"),
    ("ecommerce.coupon:update", "ecommerce.coupon", "update", "ecommerce"),
    ("ecommerce.promotion:read", "ecommerce.promotion", "read", "ecommerce"),
    ("ecommerce.promotion:create", "ecommerce.promotion", "create", "ecommerce"),
    ("ecommerce.promotion:update", "ecommerce.promotion", "update", "ecommerce"),
    ("ecommerce.marketplace:read", "ecommerce.marketplace", "read", "ecommerce"),
    ("ecommerce.marketplace:create", "ecommerce.marketplace", "create", "ecommerce"),
    ("ecommerce.marketplace:update", "ecommerce.marketplace", "update", "ecommerce"),
    ("ecommerce.marketplace:submit", "ecommerce.marketplace", "submit", "ecommerce"),
    ("ecommerce.marketplace:approve", "ecommerce.marketplace", "approve", "ecommerce"),
    ("ecommerce.marketplace:sync", "ecommerce.marketplace", "sync", "ecommerce"),
    ("ecommerce.notification:read", "ecommerce.notification", "read", "ecommerce"),
    ("ecommerce.notification:acknowledge", "ecommerce.notification", "acknowledge", "ecommerce"),
    ("ecommerce.report:read", "ecommerce.report", "read", "ecommerce"),
    ("ecommerce.report:export", "ecommerce.report", "export", "ecommerce"),
]

_ALL = [p[0] for p in ECOMMERCE_PERMISSIONS]

ECOMMERCE_ADMIN_PERMISSIONS = list(_ALL)
ECOMMERCE_MANAGER_PERMISSIONS = [
    p for p in _ALL
    if ":approve" not in p and ":reject" not in p
]
MARKETPLACE_MANAGER_PERMISSIONS = [
    p for p in _ALL
    if any(
        x in p
        for x in (
            "ecommerce.marketplace",
            "ecommerce.listing",
            "ecommerce.channel",
            "ecommerce.store:read",
            "ecommerce.report:read",
            "ecommerce.notification:read",
        )
    )
]
STORE_OPERATOR_PERMISSIONS = [
    p for p in _ALL
    if any(
        x in p
        for x in (
            "ecommerce.store",
            "ecommerce.channel",
            "ecommerce.listing",
            "ecommerce.cart",
            "ecommerce.order",
            "ecommerce.shipment",
            "ecommerce.tracking",
            "ecommerce.return",
            "ecommerce.notification",
            "ecommerce.report:read",
        )
    )
    and ":approve" not in p
]
''',
    )


def gen_api() -> None:
    w(
        ECOMMERCE / "dependencies.py",
        '''"""E-Commerce module dependencies."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from database.session import get_db
from modules.foundation.dependencies import get_tenant_context, require_permission
from modules.foundation.domain.value_objects import TenantContext

__all__ = [
    "PaginationParams",
    "get_pagination",
    "get_tenant_context",
    "require_permission",
    "TenantContext",
    "get_db",
    "paginate",
    "extract_update_fields",
]


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 25,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def paginate(items: list, pagination: PaginationParams) -> list:
    return items[pagination.offset : pagination.offset + pagination.page_size]


def extract_update_fields(body) -> dict:
    fields = body.model_dump(exclude_unset=True)
    fields.pop("version", None)
    return fields
''',
    )

    schema_lines = [
        '"""E-Commerce Pydantic schemas."""',
        "",
        "from uuid import UUID",
        "",
        "from pydantic import BaseModel, ConfigDict",
        "",
        "",
        "class OrmModel(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        schema_lines += [
            "",
            f"class {name}Create(BaseModel):",
            "    company_id: UUID | None = None",
            "    status: str | None = None",
            "",
            f"class {name}Update(BaseModel):",
            "    status: str | None = None",
            "    version: int | None = None",
            "",
            f"class {name}Response(OrmModel):",
            "    id: UUID",
            "    company_id: UUID",
            "    status: str",
            "    version: int",
        ]
    w(ECOMMERCE / "schemas.py", "\n".join(schema_lines) + "\n")

    router_parts: list[str] = [
        '"""E-Commerce API route handlers."""',
        "",
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from modules.ecommerce.dependencies import (",
        "    PaginationParams,",
        "    extract_update_fields,",
        "    get_db,",
        "    get_pagination,",
        "    paginate,",
        "    require_permission,",
        ")",
        "from modules.ecommerce.schemas import (",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_parts.append(f"    {name}Create,")
        router_parts.append(f"    {name}Response,")
        router_parts.append(f"    {name}Update,")
    router_parts += [
        ")",
        "from modules.ecommerce.service import (",
    ]
    seen_svc: set[str] = set()
    for _, _, svc, _, _ in ROUTE_SPECS:
        if svc not in seen_svc:
            router_parts.append(f"    {svc},")
            seen_svc.add(svc)
    router_parts.append(")")
    router_parts.append("from modules.foundation.domain.value_objects import TenantContext")
    router_parts.append("from shared.schemas import APIResponse")
    router_parts.append("")

    exports: list[str] = []
    route_actions: dict[str, list[tuple[str, str]]] = {
        "stores": [
            ("submit", "ecommerce.store:submit"),
            ("approve", "ecommerce.store:approve"),
        ],
        "product-listings": [
            ("submit", "ecommerce.listing:submit"),
            ("approve", "ecommerce.listing:approve"),
            ("publish", "ecommerce.listing:publish"),
        ],
        "orders": [
            ("submit", "ecommerce.order:submit"),
            ("accept", "ecommerce.order:accept"),
            ("cancel", "ecommerce.order:cancel"),
        ],
        "payments": [
            ("capture", "ecommerce.payment:capture"),
            ("refund", "ecommerce.payment:refund"),
        ],
        "return-requests": [
            ("submit", "ecommerce.return:submit"),
            ("approve", "ecommerce.return:approve"),
            ("reject", "ecommerce.return:reject"),
        ],
        "marketplace-connectors": [
            ("submit", "ecommerce.marketplace:submit"),
            ("approve", "ecommerce.marketplace:approve"),
            ("sync", "ecommerce.marketplace:sync"),
        ],
        "notifications": [
            ("acknowledge", "ecommerce.notification:acknowledge"),
        ],
    }

    for prefix, name, svc, perm, _branch in ROUTE_SPECS:
        rname = f"{prefix.replace('-', '_')}_router"
        exports.append(rname)
        router_parts.append(f'{rname} = APIRouter(prefix="/{prefix}", tags=["E-Commerce — {name}"])')
        router_parts.append("")
        create_call = f"{svc}(db).create(ctx, **body.model_dump(exclude_none=True))"
        update_perm = f"{perm}:update"
        create_perm = f"{perm}:create"
        if perm in {"ecommerce.usage"}:
            pass
        elif perm == "ecommerce.notification":
            create_perm = "ecommerce.notification:read"
            update_perm = "ecommerce.notification:read"
        elif perm == "ecommerce.monitor":
            create_perm = "ecommerce.monitor:read"
            update_perm = "ecommerce.monitor:acknowledge"
        elif perm == "ecommerce.report":
            create_perm = "ecommerce.report:read"
            update_perm = "ecommerce.report:export"
        elif perm == "ecommerce.retry":
            update_perm = "ecommerce.retry:review"
            create_perm = "ecommerce.retry:read"
        elif perm == "ecommerce.dlq":
            update_perm = "ecommerce.dlq:review"
            create_perm = "ecommerce.dlq:read"
        elif perm == "ecommerce.sync" and prefix == "sync-logs":
            create_perm = "ecommerce.sync:read"
            update_perm = "ecommerce.sync:read"
        elif perm == "ecommerce.message":
            update_perm = "ecommerce.message:requeue"

        fn = prefix.replace("-", "_")
        router_parts += [
            f'@{rname}.get("", response_model=APIResponse[list[{name}Response]])',
            f"def list_{fn}(",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    items = {svc}(db).list(ctx, company_id=company_id)",
            '    return APIResponse(message="OK", data=paginate(items, pagination))',
            "",
            f'@{rname}.get("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def get_{fn}(",
            "    row_id: UUID,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="OK", data={svc}(db).get(ctx, row_id))',
            "",
            f'@{rname}.post("", response_model=APIResponse[{name}Response])',
            f"def create_{fn}(",
            f"    body: {name}Create,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{create_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="Created", data={create_call})',
            "",
            f'@{rname}.patch("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def update_{fn}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{update_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            (
                f'    return APIResponse(message="Updated", '
                f"data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))"
            ),
            "",
        ]

        for act, pcode in route_actions.get(prefix, []):
            router_parts += [
                f'@{rname}.post("/{{row_id}}/{act}", response_model=APIResponse[{name}Response])',
                f"def {act}_{fn}(",
                "    row_id: UUID,",
                f'    ctx: Annotated[TenantContext, Depends(require_permission("{pcode}"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f'    return APIResponse(message="{act}", data={svc}(db).{act}(ctx, row_id))',
                "",
            ]

    w(ECOMMERCE / "routers" / "__init__.py", "\n".join(router_parts) + "\n")

    import_list = ",\n    ".join(exports)
    include_lines = "\n".join(f"ecommerce_router.include_router({e})" for e in exports)
    w(
        ECOMMERCE / "router.py",
        f'''"""E-Commerce module router aggregation."""

from fastapi import APIRouter

from modules.ecommerce.routers import (
    {import_list},
)

ecommerce_router = APIRouter(prefix="/ecommerce")
{include_lines}
''',
    )


def gen_tasks_tests() -> None:
    w(
        ECOMMERCE / "tasks.py",
        '''"""E-Commerce Celery task stubs per ERD_22 section 11."""

from workers.celery_app import celery_app


@celery_app.task(name="ecommerce.listing_publish_scheduler")
def listing_publish_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.ecommerce.models import EcProductListing

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(EcProductListing).where(
                    EcProductListing.is_deleted.is_(False),
                    EcProductListing.status == "approved",
                )
            ).all()
        )
        return {"status": "ok", "listings_due": len(rows)}
    finally:
        db.close()


@celery_app.task(name="ecommerce.inventory_sync_pull")
def inventory_sync_pull() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.ecommerce.models import EcListingInventory

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(EcListingInventory).where(
                    EcListingInventory.is_deleted.is_(False),
                    EcListingInventory.sync_status.in_(["pending", "stale", "failed"]),
                )
            ).all()
        )
        return {"status": "ok", "projections_due": len(rows)}
    finally:
        db.close()


@celery_app.task(name="ecommerce.order_import_poller")
def order_import_poller() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.ecommerce.models import EcMarketplaceConnector

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(EcMarketplaceConnector).where(
                    EcMarketplaceConnector.is_deleted.is_(False),
                    EcMarketplaceConnector.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "connectors": len(rows)}
    finally:
        db.close()


@celery_app.task(name="ecommerce.sales_order_mapper")
def sales_order_mapper() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.ecommerce.models import EcOrder

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(EcOrder).where(
                    EcOrder.is_deleted.is_(False),
                    EcOrder.status == "accepted",
                    EcOrder.sales_order_id.is_(None),
                )
            ).all()
        )
        return {"status": "ok", "orders_to_map": len(rows)}
    finally:
        db.close()


@celery_app.task(name="ecommerce.shipment_tracking_poller")
def shipment_tracking_poller() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.ecommerce.models import EcShipment

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(EcShipment).where(
                    EcShipment.is_deleted.is_(False),
                    EcShipment.status.in_(["shipped", "in_transit"]),
                )
            ).all()
        )
        return {"status": "ok", "shipments": len(rows)}
    finally:
        db.close()


@celery_app.task(name="ecommerce.cart_abandonment_notifier")
def cart_abandonment_notifier() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.ecommerce.models import EcCustomerCart

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(EcCustomerCart).where(
                    EcCustomerCart.is_deleted.is_(False),
                    EcCustomerCart.status == "open",
                )
            ).all()
        )
        return {"status": "ok", "open_carts": len(rows)}
    finally:
        db.close()

''',
    )

    w(
        TESTS / "unit" / "ecommerce" / "test_ec_hub_engines.py",
        '''"""Unit tests for E-Commerce engines."""

from types import SimpleNamespace

from modules.ecommerce.service.engines import (
    MarketplaceConnectorEngine,
    OrderEngine,
    ProductListingEngine,
    ReturnRequestEngine,
    StoreEngine,
)


def test_store_lifecycle():
    row = SimpleNamespace(status="draft")
    eng = StoreEngine()
    eng.submit(row)
    assert row.status == "submitted"
    eng.approve(row)
    assert row.status == "approved"


def test_product_listing_lifecycle():
    row = SimpleNamespace(status="draft")
    eng = ProductListingEngine()
    eng.submit(row)
    eng.approve(row)
    eng.publish(row)
    assert row.status == "published"


def test_order_lifecycle():
    row = SimpleNamespace(status="new")
    eng = OrderEngine()
    eng.submit(row)
    eng.accept(row)
    assert row.status == "accepted"


def test_return_request_lifecycle():
    row = SimpleNamespace(status="requested")
    eng = ReturnRequestEngine()
    eng.submit(row)
    eng.approve(row)
    assert row.status == "approved"


def test_marketplace_connector_sync():
    row = SimpleNamespace(status="draft")
    eng = MarketplaceConnectorEngine()
    eng.submit(row)
    eng.approve(row)
    eng.sync(row)
    assert row.status == "active"
''',
    )
    w(
        TESTS / "unit" / "ecommerce" / "test_ec_hub_tasks.py",
        '''"""Unit tests for E-Commerce Celery task names."""

from modules.ecommerce import tasks


def test_ecommerce_task_names_registered():
    assert tasks.listing_publish_scheduler.name == "ecommerce.listing_publish_scheduler"
    assert tasks.inventory_sync_pull.name == "ecommerce.inventory_sync_pull"
    assert tasks.order_import_poller.name == "ecommerce.order_import_poller"
    assert tasks.sales_order_mapper.name == "ecommerce.sales_order_mapper"
    assert tasks.shipment_tracking_poller.name == "ecommerce.shipment_tracking_poller"
    assert tasks.cart_abandonment_notifier.name == "ecommerce.cart_abandonment_notifier"
''',
    )
    w(
        TESTS / "security" / "ecommerce" / "test_ec_hub_permissions.py",
        '''"""Security tests for E-Commerce permissions."""

from modules.ecommerce.permissions import (
    ECOMMERCE_ADMIN_PERMISSIONS,
    ECOMMERCE_MANAGER_PERMISSIONS,
    ECOMMERCE_PERMISSIONS,
    MARKETPLACE_MANAGER_PERMISSIONS,
    STORE_OPERATOR_PERMISSIONS,
)


def test_ecommerce_permissions_defined():
    codes = [p[0] for p in ECOMMERCE_PERMISSIONS]
    assert "ecommerce.store:approve" in codes
    assert "ecommerce.order:accept" in codes
    assert "ecommerce.marketplace:sync" in codes


def test_ecommerce_roles():
    assert len(ECOMMERCE_ADMIN_PERMISSIONS) == len(ECOMMERCE_PERMISSIONS)
    assert any("listing" in p for p in ECOMMERCE_MANAGER_PERMISSIONS)
    assert any("marketplace" in p for p in MARKETPLACE_MANAGER_PERMISSIONS)
    assert any("order" in p for p in STORE_OPERATOR_PERMISSIONS)
''',
    )
    w(
        TESTS / "integration" / "ecommerce" / "test_ec_hub_module_import.py",
        '''"""E-Commerce module import smoke tests."""

from modules.ecommerce.models import EcOrder, EcProductListing, EcStore
from modules.ecommerce.router import ecommerce_router
from modules.ecommerce.service import (
    EcommerceIntegrationService,
    OrderService,
    ProductListingService,
    StoreService,
)
from modules.ecommerce.service.engines import OrderEngine, ProductListingEngine, StoreEngine


def test_ecommerce_models_importable():
    assert EcStore is not None
    assert EcProductListing is not None
    assert EcOrder is not None


def test_ecommerce_router_mounted():
    assert ecommerce_router.prefix == "/ecommerce"
    assert len(ecommerce_router.routes) > 0


def test_ecommerce_services_and_engines_importable():
    assert StoreService is not None
    assert ProductListingService is not None
    assert OrderService is not None
    assert EcommerceIntegrationService is not None
    assert StoreEngine is not None
    assert ProductListingEngine is not None
    assert OrderEngine is not None
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0419_seed_ec_permissions.py",
        '''"""Seed E-Commerce permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.permissions import (
    MARKETPLACE_MANAGER_PERMISSIONS,
    ECOMMERCE_ADMIN_PERMISSIONS,
    ECOMMERCE_MANAGER_PERMISSIONS,
    ECOMMERCE_PERMISSIONS,
    STORE_OPERATOR_PERMISSIONS,
)

revision: str = "0419_seed_ec_permissions"
down_revision: str | None = "0418_ec_report"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)

ROLE_SPECS: list[tuple[str, str, list[str]]] = [
    ("ECOMMERCE_ADMIN", "E-Commerce Admin", ECOMMERCE_ADMIN_PERMISSIONS),
    ("ECOMMERCE_MANAGER", "E-Commerce Manager", ECOMMERCE_MANAGER_PERMISSIONS),
    ("MARKETPLACE_MANAGER", "Marketplace Manager", MARKETPLACE_MANAGER_PERMISSIONS),
    ("STORE_OPERATOR", "Store Operator", STORE_OPERATOR_PERMISSIONS),
]


def _ensure_permission(conn, now, code, resource, action, module):
    exists = conn.execute(
        sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
        {"code": code},
    ).first()
    if exists:
        return str(exists[0])
    perm_id = str(uuid4())
    conn.execute(
        sa.insert(PERMISSION_TABLE).values(
            id=perm_id,
            permission_code=code,
            resource=resource,
            action=action,
            module=module,
            is_active=True,
            created_at=now,
        )
    )
    return perm_id


def _ensure_role(conn, now, tenant_id, role_code, role_name):
    exists = conn.execute(
        sa.text(
            """
            SELECT id FROM foundation.sec_role
            WHERE tenant_id = :tid AND role_code = :code AND is_deleted = false
            """
        ),
        {"tid": tenant_id, "code": role_code},
    ).first()
    if exists:
        return str(exists[0])
    role_id = str(uuid4())
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role
            (id, tenant_id, role_code, role_name, is_system_role, status,
             created_at, updated_at, is_deleted, version)
            VALUES (:id, :tid, :code, :name, true, 'active', :now, :now, false, 1)
            """
        ),
        {"id": role_id, "tid": tenant_id, "code": role_code, "name": role_name, "now": now},
    )
    return role_id


def _grant(conn, now, tenant_id, role_id, perm_id):
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM foundation.sec_role_permission
            WHERE role_id = :rid AND permission_id = :pid
            """
        ),
        {"rid": role_id, "pid": perm_id},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role_permission
            (id, tenant_id, role_id, permission_id, granted_at)
            VALUES (:id, :tid, :rid, :pid, :now)
            """
        ),
        {"id": str(uuid4()), "tid": tenant_id, "rid": role_id, "pid": perm_id, "now": now},
    )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    perm_ids: dict[str, str] = {}
    for code, resource, action, module in ECOMMERCE_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, perms in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for perm_code in perms:
                _grant(conn, now, tid, role_id, perm_ids[perm_code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in reversed(ROLE_SPECS):
        conn.execute(
            sa.text(
                "DELETE FROM foundation.sec_role WHERE role_code = :code AND is_system_role = true"
            ),
            {"code": role_code},
        )
    for code, _, _, _ in ECOMMERCE_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0420_seed_ecommerce_workflows.py",
        '''"""Seed E-Commerce workflow definitions per ERD_22."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0420_seed_ecommerce_workflows"
down_revision: str | None = "0419_seed_ec_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "EC_STORE_APPROVAL",
        "E-Commerce Store Approval",
        "ec_store",
        [
            (1, "STORE_OPERATOR", "Store Operator Submit", "role"),
            (2, "ECOMMERCE_MANAGER", "E-Commerce Manager Approval", "role"),
            (3, "ECOMMERCE_ADMIN", "E-Commerce Admin Approval", "role"),
        ],
    ),
    (
        "EC_LISTING_APPROVAL",
        "E-Commerce Listing Approval",
        "ec_product_listing",
        [
            (1, "STORE_OPERATOR", "Store Operator Submit", "role"),
            (2, "MARKETPLACE_MANAGER", "Marketplace Manager Approval", "role"),
            (3, "ECOMMERCE_ADMIN", "E-Commerce Admin Approval", "role"),
        ],
    ),
    (
        "EC_ORDER_REVIEW",
        "E-Commerce Order Review",
        "ec_order",
        [
            (1, "STORE_OPERATOR", "Store Operator Submit", "role"),
            (2, "ECOMMERCE_MANAGER", "E-Commerce Manager Review", "role"),
        ],
    ),
    (
        "EC_RETURN_APPROVAL",
        "E-Commerce Return Approval",
        "ec_return_request",
        [
            (1, "STORE_OPERATOR", "Store Operator Submit", "role"),
            (2, "ECOMMERCE_MANAGER", "E-Commerce Manager Approval", "role"),
            (3, "ECOMMERCE_ADMIN", "E-Commerce Admin Approval", "role"),
        ],
    ),
    (
        "EC_MARKETPLACE_SYNC",
        "E-Commerce Marketplace Sync Approval",
        "ec_marketplace_connector",
        [
            (1, "MARKETPLACE_MANAGER", "Marketplace Manager Submit", "role"),
            (2, "ECOMMERCE_MANAGER", "E-Commerce Manager Approval", "role"),
            (3, "ECOMMERCE_ADMIN", "E-Commerce Admin Approval", "role"),
        ],
    ),
]
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'integration', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
                        "atype": approver_type,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
''',
    )


def gen_wiring() -> None:
    patch_file(
        SHARED / "router.py",
        "from modules.integration.router import integration_router\n",
        "from modules.integration.router import integration_router\n"
        "from modules.ecommerce.router import ecommerce_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(integration_router)\n",
        "api_v1_router.include_router(integration_router)\n"
        "api_v1_router.include_router(ecommerce_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.integration.models  # noqa: F401 — register ORM metadata\n",
        "import modules.integration.models  # noqa: F401 — register ORM metadata\n"
        "import modules.ecommerce.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.integration",\n',
        '        "modules.integration",\n        "modules.ecommerce",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.integration.*",\n',
        '    "modules.integration.*",\n    "modules.ecommerce.*",\n',
    )
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ruff_marker = (
        '"src/modules/integration/**" = ["E501", "SIM102"]\n'
        '"src/modules/integration/domain/enums.py" = ["UP042"]\n'
    )
    ruff_new = (
        ruff_marker
        + '"src/modules/ecommerce/**" = ["E501", "SIM102"]\n'
        + '"src/modules/ecommerce/domain/enums.py" = ["UP042"]\n'
    )
    if ruff_marker in pyproject and '"src/modules/ecommerce/**"' not in pyproject:
        patch_file(ROOT / "pyproject.toml", ruff_marker, ruff_new)
    elif '"src/modules/ecommerce/**"' not in pyproject:
        alt = '"src/modules/integration/domain/enums.py" = ["UP042"]\n'
        if alt in pyproject:
            patch_file(
                ROOT / "pyproject.toml",
                alt,
                alt
                + '"src/modules/ecommerce/**" = ["E501", "SIM102"]\n'
                + '"src/modules/ecommerce/domain/enums.py" = ["UP042"]\n',
            )




def main() -> None:
    gen_scaffold()
    gen_domain()
    gen_models()
    gen_migrations()
    gen_repos()
    gen_engines()
    gen_services()
    gen_adapters()
    gen_permissions()
    gen_api()
    gen_tasks_tests()
    gen_seeds()
    gen_wiring()
    print(f"OK ecommerce module generated — {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0420_seed_ecommerce_workflows")


if __name__ == "__main__":
    main()
