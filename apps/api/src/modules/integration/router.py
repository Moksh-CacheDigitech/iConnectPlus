"""Integration module router aggregation."""

from fastapi import APIRouter

from modules.integration.routers import (
    api_credentials_router,
    api_usages_router,
    connectors_router,
    data_mappings_router,
    data_transformations_router,
    dead_letters_router,
    event_definitions_router,
    event_subscriptions_router,
    external_systems_router,
    message_queues_router,
    messages_router,
    monitors_router,
    notifications_router,
    oauth_clients_router,
    rate_limits_router,
    reports_router,
    retry_queues_router,
    sync_jobs_router,
    sync_logs_router,
    webhooks_router,
)

integration_router = APIRouter(prefix="/integration")
integration_router.include_router(external_systems_router)
integration_router.include_router(connectors_router)
integration_router.include_router(api_credentials_router)
integration_router.include_router(oauth_clients_router)
integration_router.include_router(webhooks_router)
integration_router.include_router(event_definitions_router)
integration_router.include_router(event_subscriptions_router)
integration_router.include_router(message_queues_router)
integration_router.include_router(messages_router)
integration_router.include_router(retry_queues_router)
integration_router.include_router(dead_letters_router)
integration_router.include_router(data_mappings_router)
integration_router.include_router(data_transformations_router)
integration_router.include_router(sync_jobs_router)
integration_router.include_router(sync_logs_router)
integration_router.include_router(api_usages_router)
integration_router.include_router(rate_limits_router)
integration_router.include_router(notifications_router)
integration_router.include_router(monitors_router)
integration_router.include_router(reports_router)
