"""Payroll domain exceptions."""

from core.exceptions import ConflictException


class InvalidPayrollPeriodState(ConflictException):
    def __init__(self, message: str = "Invalid payroll period state") -> None:
        super().__init__(message)

class InvalidSalaryStructureState(ConflictException):
    def __init__(self, message: str = "Invalid salarystructure state") -> None:
        super().__init__(message)

class InvalidSalaryComponentState(ConflictException):
    def __init__(self, message: str = "Invalid salarycomponent state") -> None:
        super().__init__(message)

class InvalidSalaryStructureLineState(ConflictException):
    def __init__(self, message: str = "Invalid salarystructureline state") -> None:
        super().__init__(message)

class InvalidEmployeeSalaryState(ConflictException):
    def __init__(self, message: str = "Invalid employeesalary state") -> None:
        super().__init__(message)

class InvalidEmployeeSalaryComponentState(ConflictException):
    def __init__(self, message: str = "Invalid employeesalarycomponent state") -> None:
        super().__init__(message)

class InvalidEarningTypeState(ConflictException):
    def __init__(self, message: str = "Invalid earningtype state") -> None:
        super().__init__(message)

class InvalidDeductionTypeState(ConflictException):
    def __init__(self, message: str = "Invalid deductiontype state") -> None:
        super().__init__(message)

class InvalidPayrollRunState(ConflictException):
    def __init__(self, message: str = "Invalid payroll run state") -> None:
        super().__init__(message)

class InvalidPayrollRunLineState(ConflictException):
    def __init__(self, message: str = "Invalid payroll runline state") -> None:
        super().__init__(message)

class InvalidPayslipState(ConflictException):
    def __init__(self, message: str = "Invalid payslip state") -> None:
        super().__init__(message)

class InvalidTaxConfigurationState(ConflictException):
    def __init__(self, message: str = "Invalid taxconfiguration state") -> None:
        super().__init__(message)

class InvalidStatutoryContributionState(ConflictException):
    def __init__(self, message: str = "Invalid statutorycontribution state") -> None:
        super().__init__(message)

class InvalidBonusState(ConflictException):
    def __init__(self, message: str = "Invalid bonus state") -> None:
        super().__init__(message)

class InvalidReimbursementState(ConflictException):
    def __init__(self, message: str = "Invalid reimbursement state") -> None:
        super().__init__(message)

class InvalidLoanState(ConflictException):
    def __init__(self, message: str = "Invalid loan state") -> None:
        super().__init__(message)

class InvalidLoanInstallmentState(ConflictException):
    def __init__(self, message: str = "Invalid loaninstallment state") -> None:
        super().__init__(message)

class InvalidPayrollAdjustmentState(ConflictException):
    def __init__(self, message: str = "Invalid payroll adjustment state") -> None:
        super().__init__(message)

class InvalidPayrollPostingState(ConflictException):
    def __init__(self, message: str = "Invalid payroll posting state") -> None:
        super().__init__(message)

class InvalidPayrollSummaryState(ConflictException):
    def __init__(self, message: str = "Invalid payroll summary state") -> None:
        super().__init__(message)
