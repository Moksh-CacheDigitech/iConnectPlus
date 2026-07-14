"""Payroll Pydantic schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PayrollPeriodCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class PayrollPeriodUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayrollPeriodResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class SalaryStructureCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class SalaryStructureUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class SalaryStructureResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class SalaryComponentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class SalaryComponentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class SalaryComponentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class SalaryStructureLineCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class SalaryStructureLineUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class SalaryStructureLineResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class EmployeeSalaryCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class EmployeeSalaryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class EmployeeSalaryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int


class EmployeeSalaryComponentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_salary_id: UUID
    employee_id: UUID
    salary_component_id: UUID
    amount: Decimal | None = None
    percent: Decimal | None = None
    override_flag: bool = False
    status: str | None = None


class EmployeeSalaryComponentUpdate(BaseModel):
    amount: Decimal | None = None
    percent: Decimal | None = None
    override_flag: bool | None = None
    status: str | None = None
    version: int | None = None


class EmployeeSalaryComponentResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    employee_salary_id: UUID
    employee_id: UUID
    salary_component_id: UUID
    status: str
    version: int


class PayrollPostingPostRequest(BaseModel):
    debit_account_id: UUID
    credit_account_id: UUID


class EarningTypeCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class EarningTypeUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class EarningTypeResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class DeductionTypeCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class DeductionTypeUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class DeductionTypeResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class TaxConfigurationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class TaxConfigurationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class TaxConfigurationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class StatutoryContributionCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class StatutoryContributionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class StatutoryContributionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PayrollRunCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class PayrollRunUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayrollRunResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PayrollRunLineCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class PayrollRunLineUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayrollRunLineResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PayslipCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class PayslipUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayslipResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class BonusCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class BonusUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class BonusResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ReimbursementCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ReimbursementUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ReimbursementResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class LoanCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class LoanUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class LoanResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class LoanInstallmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class LoanInstallmentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class LoanInstallmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PayrollAdjustmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class PayrollAdjustmentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayrollAdjustmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PayrollPostingCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class PayrollPostingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayrollPostingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class PayrollSummaryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class PayrollSummaryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class PayrollSummaryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int
