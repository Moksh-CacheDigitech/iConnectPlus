"""Service adapters."""

from modules.service.adapters.asset_port import ServiceAssetAdapter
from modules.service.adapters.finance_port import ServiceFinanceAdapter
from modules.service.adapters.master_data_port import ServiceMasterDataAdapter
from modules.service.adapters.organization_port import ServiceOrganizationAdapter
from modules.service.adapters.payroll_port import ServicePayrollAdapter

__all__ = [
    "ServiceAssetAdapter",
    "ServiceFinanceAdapter",
    "ServiceMasterDataAdapter",
    "ServiceOrganizationAdapter",
    "ServicePayrollAdapter",
]
