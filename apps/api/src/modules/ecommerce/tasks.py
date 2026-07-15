"""E-Commerce Celery task stubs per ERD_22 section 11."""

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

