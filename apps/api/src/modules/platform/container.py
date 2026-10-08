"""DI factory — obtain all platform ports from a Session."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

@dataclass(slots=True)
class PlatformPorts:
    finance: object
    inventory: object
    master_data: object
    workflow: object
    notify: object
    audit: object
    numbering: object
    outbox: object
    integration: object


def get_platform_ports(db: Session) -> PlatformPorts:
    """Construct platform ports for the current request/unit-of-work."""
    # Local imports keep Celery autodiscover free of circular import chains.
    from modules.platform.adapters.audit_adapter import AuditAdapter
    from modules.platform.adapters.finance_adapter import FinancePostingAdapter
    from modules.platform.adapters.integration_adapter import IntegrationGatewayAdapter
    from modules.platform.adapters.inventory_adapter import InventoryStockAdapter
    from modules.platform.adapters.master_data_adapter import MasterDataLookupAdapter
    from modules.platform.adapters.numbering_adapter import DocumentNumberingAdapter
    from modules.platform.adapters.notify_adapter import NotifyAdapter
    from modules.platform.adapters.workflow_adapter import WorkflowAdapter
    from modules.platform.outbox.service import OutboxService

    return PlatformPorts(
        finance=FinancePostingAdapter(db),
        inventory=InventoryStockAdapter(db),
        master_data=MasterDataLookupAdapter(db),
        workflow=WorkflowAdapter(db),
        notify=NotifyAdapter(db),
        audit=AuditAdapter(db),
        numbering=DocumentNumberingAdapter(db),
        outbox=OutboxService(db),
        integration=IntegrationGatewayAdapter(db),
    )
