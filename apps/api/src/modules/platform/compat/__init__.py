"""Drop-in facades so modules can swap to platform ports with minimal churn."""

from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.platform.compat.notify_facade import PlatformNotifyFacade

__all__ = ["PlatformAuditFacade", "PlatformNotifyFacade"]
