"""Integration Hub module import smoke tests."""

from modules.integration.models import IntConnector, IntExternalSystem, IntSyncJob
from modules.integration.router import integration_router
from modules.integration.service import (
    ConnectorService,
    ExternalSystemService,
    IntegrationIntegrationService,
    SyncJobService,
)
from modules.integration.service.engines import ConnectorEngine, ExternalSystemEngine, SyncJobEngine


def test_integration_models_importable():
    assert IntExternalSystem is not None
    assert IntConnector is not None
    assert IntSyncJob is not None


def test_integration_router_mounted():
    assert integration_router.prefix == "/integration"
    assert len(integration_router.routes) > 0


def test_integration_services_and_engines_importable():
    assert ExternalSystemService is not None
    assert ConnectorService is not None
    assert SyncJobService is not None
    assert IntegrationIntegrationService is not None
    assert ExternalSystemEngine is not None
    assert ConnectorEngine is not None
    assert SyncJobEngine is not None
