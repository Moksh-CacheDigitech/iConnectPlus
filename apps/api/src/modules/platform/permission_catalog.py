"""Single permission catalog assembled from every module's ``permissions.py``."""

from __future__ import annotations

from modules.analytics import permissions as analytics_permissions
from modules.asset import permissions as asset_permissions
from modules.crm import permissions as crm_permissions
from modules.document import permissions as document_permissions
from modules.ecommerce import permissions as ecommerce_permissions
from modules.finance import permissions as finance_permissions
from modules.foundation import permissions as foundation_permissions
from modules.grc import permissions as grc_permissions
from modules.helpdesk import permissions as helpdesk_permissions
from modules.hr import permissions as hr_permissions
from modules.integration import permissions as integration_permissions
from modules.inventory import permissions as inventory_permissions
from modules.manufacturing import permissions as manufacturing_permissions
from modules.marketing import permissions as marketing_permissions
from modules.master_data import permissions as master_data_permissions
from modules.organization import permissions as organization_permissions
from modules.payroll import permissions as payroll_permissions
from modules.platform import permissions as platform_permissions
from modules.portal import permissions as portal_permissions
from modules.procurement import permissions as procurement_permissions
from modules.project import permissions as project_permissions
from modules.quality import permissions as quality_permissions
from modules.recruitment import permissions as recruitment_permissions
from modules.sales import permissions as sales_permissions
from modules.service import permissions as service_permissions

_PERMISSION_MODULES = (
    analytics_permissions,
    asset_permissions,
    crm_permissions,
    document_permissions,
    ecommerce_permissions,
    finance_permissions,
    foundation_permissions,
    grc_permissions,
    helpdesk_permissions,
    hr_permissions,
    integration_permissions,
    inventory_permissions,
    manufacturing_permissions,
    marketing_permissions,
    master_data_permissions,
    organization_permissions,
    payroll_permissions,
    platform_permissions,
    portal_permissions,
    procurement_permissions,
    project_permissions,
    quality_permissions,
    recruitment_permissions,
    sales_permissions,
    service_permissions,
)


def all_permission_entries() -> list[tuple[str, str, str, str]]:
    """(permission_code, resource, action, module) across all modules, de-duplicated."""
    seen: dict[str, tuple[str, str, str, str]] = {}
    for mod in _PERMISSION_MODULES:
        for name, value in vars(mod).items():
            if not (name.isupper() and isinstance(value, list)):
                continue
            for item in value:
                if isinstance(item, tuple) and len(item) == 4 and isinstance(item[0], str):
                    seen.setdefault(item[0], item)
    return list(seen.values())


def all_permission_codes() -> set[str]:
    return {entry[0] for entry in all_permission_entries()}
