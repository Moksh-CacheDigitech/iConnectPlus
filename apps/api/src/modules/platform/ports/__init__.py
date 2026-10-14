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
    # Explicit per-symbol imports keep lazy-load without dynamic module names.
    if name == "IAudit":
        from modules.platform.ports.audit import IAudit

        return IAudit
    if name == "IDocumentNumbering":
        from modules.platform.ports.numbering import IDocumentNumbering

        return IDocumentNumbering
    if name == "IFinancePosting":
        from modules.platform.ports.finance import IFinancePosting

        return IFinancePosting
    if name == "IIntegrationGateway":
        from modules.platform.ports.integration import IIntegrationGateway

        return IIntegrationGateway
    if name == "IInventoryStock":
        from modules.platform.ports.inventory import IInventoryStock

        return IInventoryStock
    if name == "IMasterDataLookup":
        from modules.platform.ports.master_data import IMasterDataLookup

        return IMasterDataLookup
    if name == "INotify":
        from modules.platform.ports.notify import INotify

        return INotify
    if name == "IOutbox":
        from modules.platform.ports.outbox import IOutbox

        return IOutbox
    if name == "IWorkflow":
        from modules.platform.ports.workflow import IWorkflow

        return IWorkflow
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
