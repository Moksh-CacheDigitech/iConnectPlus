"""E-Commerce permission constants per ERD_22 section 10."""

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
