"""Platform port protocols — the only allowed cross-domain seams."""

__all__ = [
    "IAudit",
    "IDocumentNumbering",
    "IFinancePosting",
    "IIntegrationGateway",
    "IInventoryStock",
    "IMasterDataLookup",
    "INotify",
    "IOutbox",
    "IWorkflow",
]


def __getattr__(name: str):
    mapping = {
        "IAudit": "modules.platform.ports.audit",
        "IDocumentNumbering": "modules.platform.ports.numbering",
        "IFinancePosting": "modules.platform.ports.finance",
        "IIntegrationGateway": "modules.platform.ports.integration",
        "IInventoryStock": "modules.platform.ports.inventory",
        "IMasterDataLookup": "modules.platform.ports.master_data",
        "INotify": "modules.platform.ports.notify",
        "IOutbox": "modules.platform.ports.outbox",
        "IWorkflow": "modules.platform.ports.workflow",
    }
    if name not in mapping:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    mod = importlib.import_module(mapping[name])
    return getattr(mod, name)
