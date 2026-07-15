"""E-Commerce application service facade."""

from sqlalchemy.orm import Session

from modules.ecommerce.service.cart_item_service import CartItemService
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
from modules.ecommerce.service.store_service import StoreService


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
