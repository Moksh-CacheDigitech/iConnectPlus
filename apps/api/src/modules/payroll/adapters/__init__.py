"""Payroll adapters."""

from modules.payroll.adapters.finance_port import PayrollFinanceAdapter
from modules.payroll.adapters.hr_port import PayrollHrAdapter
from modules.payroll.adapters.master_data_port import PayrollMasterDataAdapter
from modules.payroll.adapters.organization_port import PayrollOrganizationAdapter

__all__ = [
    "PayrollFinanceAdapter",
    "PayrollHrAdapter",
    "PayrollMasterDataAdapter",
    "PayrollOrganizationAdapter",
]
