"""E-Commerce domain enums per ERD_22 section 8."""

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
