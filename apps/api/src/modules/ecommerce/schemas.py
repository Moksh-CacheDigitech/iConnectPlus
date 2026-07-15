"""E-Commerce Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StoreCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class StoreUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class StoreResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class SalesChannelCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class SalesChannelUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class SalesChannelResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProductListingCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProductListingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProductListingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ListingPriceCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ListingPriceUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ListingPriceResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ListingInventoryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ListingInventoryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ListingInventoryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class CustomerCartCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class CustomerCartUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class CustomerCartResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class CartItemCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class CartItemUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class CartItemResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OrderCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class OrderUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OrderResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OrderItemCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class OrderItemUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OrderItemResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PaymentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class PaymentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PaymentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PaymentTransactionCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class PaymentTransactionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PaymentTransactionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ShipmentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ShipmentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ShipmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ShippingTrackingCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ShippingTrackingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ShippingTrackingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ReturnRequestCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ReturnRequestUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ReturnRequestResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ReturnItemCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ReturnItemUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ReturnItemResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class CouponCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class CouponUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class CouponResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PromotionCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class PromotionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PromotionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class MarketplaceConnectorCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class MarketplaceConnectorUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class MarketplaceConnectorResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class NotificationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class NotificationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class NotificationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ReportCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ReportUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ReportResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int
