"""Concrete adapters implementing platform ports against domain services.

Import adapters from their modules directly to avoid import cycles:

    from modules.platform.adapters.finance_adapter import FinancePostingAdapter
"""

__all__ = [
    "AuditAdapter",
    "DocumentNumberingAdapter",
    "FinancePostingAdapter",
    "IntegrationGatewayAdapter",
    "InventoryStockAdapter",
    "MasterDataLookupAdapter",
    "NotifyAdapter",
    "WorkflowAdapter",
]


def __getattr__(name: str):
    # Explicit per-symbol imports keep lazy-load without dynamic module names.
    if name == "AuditAdapter":
        from modules.platform.adapters.audit_adapter import AuditAdapter

        return AuditAdapter
    if name == "DocumentNumberingAdapter":
        from modules.platform.adapters.numbering_adapter import DocumentNumberingAdapter

        return DocumentNumberingAdapter
    if name == "FinancePostingAdapter":
        from modules.platform.adapters.finance_adapter import FinancePostingAdapter

        return FinancePostingAdapter
    if name == "IntegrationGatewayAdapter":
        from modules.platform.adapters.integration_adapter import IntegrationGatewayAdapter

        return IntegrationGatewayAdapter
    if name == "InventoryStockAdapter":
        from modules.platform.adapters.inventory_adapter import InventoryStockAdapter

        return InventoryStockAdapter
    if name == "MasterDataLookupAdapter":
        from modules.platform.adapters.master_data_adapter import MasterDataLookupAdapter

        return MasterDataLookupAdapter
    if name == "NotifyAdapter":
        from modules.platform.adapters.notify_adapter import NotifyAdapter

        return NotifyAdapter
    if name == "WorkflowAdapter":
        from modules.platform.adapters.workflow_adapter import WorkflowAdapter

        return WorkflowAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
