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
    mapping = {
        "AuditAdapter": "modules.platform.adapters.audit_adapter",
        "DocumentNumberingAdapter": "modules.platform.adapters.numbering_adapter",
        "FinancePostingAdapter": "modules.platform.adapters.finance_adapter",
        "IntegrationGatewayAdapter": "modules.platform.adapters.integration_adapter",
        "InventoryStockAdapter": "modules.platform.adapters.inventory_adapter",
        "MasterDataLookupAdapter": "modules.platform.adapters.master_data_adapter",
        "NotifyAdapter": "modules.platform.adapters.notify_adapter",
        "WorkflowAdapter": "modules.platform.adapters.workflow_adapter",
    }
    if name not in mapping:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    mod = importlib.import_module(mapping[name])
    return getattr(mod, name)
