"""E-Commerce domain exceptions."""

from core.exceptions import ConflictException


class InvalidStoreState(ConflictException):
    def __init__(self, message: str = "Invalid store state") -> None:
        super().__init__(message)

class InvalidSalesChannelState(ConflictException):
    def __init__(self, message: str = "Invalid saleschannel state") -> None:
        super().__init__(message)

class InvalidProductListingState(ConflictException):
    def __init__(self, message: str = "Invalid productlisting state") -> None:
        super().__init__(message)

class InvalidListingPriceState(ConflictException):
    def __init__(self, message: str = "Invalid listingprice state") -> None:
        super().__init__(message)

class InvalidListingInventoryState(ConflictException):
    def __init__(self, message: str = "Invalid listinginventory state") -> None:
        super().__init__(message)

class InvalidCustomerCartState(ConflictException):
    def __init__(self, message: str = "Invalid customercart state") -> None:
        super().__init__(message)

class InvalidCartItemState(ConflictException):
    def __init__(self, message: str = "Invalid cartitem state") -> None:
        super().__init__(message)

class InvalidOrderState(ConflictException):
    def __init__(self, message: str = "Invalid order state") -> None:
        super().__init__(message)

class InvalidOrderItemState(ConflictException):
    def __init__(self, message: str = "Invalid orderitem state") -> None:
        super().__init__(message)

class InvalidPaymentState(ConflictException):
    def __init__(self, message: str = "Invalid payment state") -> None:
        super().__init__(message)

class InvalidPaymentTransactionState(ConflictException):
    def __init__(self, message: str = "Invalid paymenttransaction state") -> None:
        super().__init__(message)

class InvalidShipmentState(ConflictException):
    def __init__(self, message: str = "Invalid shipment state") -> None:
        super().__init__(message)

class InvalidShippingTrackingState(ConflictException):
    def __init__(self, message: str = "Invalid shippingtracking state") -> None:
        super().__init__(message)

class InvalidReturnRequestState(ConflictException):
    def __init__(self, message: str = "Invalid returnrequest state") -> None:
        super().__init__(message)

class InvalidReturnItemState(ConflictException):
    def __init__(self, message: str = "Invalid returnitem state") -> None:
        super().__init__(message)

class InvalidCouponState(ConflictException):
    def __init__(self, message: str = "Invalid coupon state") -> None:
        super().__init__(message)

class InvalidPromotionState(ConflictException):
    def __init__(self, message: str = "Invalid promotion state") -> None:
        super().__init__(message)

class InvalidMarketplaceConnectorState(ConflictException):
    def __init__(self, message: str = "Invalid marketplaceconnector state") -> None:
        super().__init__(message)

class InvalidNotificationState(ConflictException):
    def __init__(self, message: str = "Invalid notification state") -> None:
        super().__init__(message)

class InvalidReportState(ConflictException):
    def __init__(self, message: str = "Invalid report state") -> None:
        super().__init__(message)
