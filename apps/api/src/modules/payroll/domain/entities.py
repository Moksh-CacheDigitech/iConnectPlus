"""Payroll domain entity markers (aggregates map 1:1 to ORM headers)."""

from enum import Enum


class PayAggregate(str, Enum):
    PAYROLLPERIOD = "pay_payroll_period"
    SALARYSTRUCTURE = "pay_salary_structure"
    SALARYCOMPONENT = "pay_salary_component"
    SALARYSTRUCTURELINE = "pay_salary_structure_line"
    EMPLOYEESALARY = "pay_employee_salary"
    EMPLOYEESALARYCOMPONENT = "pay_employee_salary_component"
    EARNINGTYPE = "pay_earning_type"
    DEDUCTIONTYPE = "pay_deduction_type"
    PAYROLLRUN = "pay_payroll_run"
    PAYROLLRUNLINE = "pay_payroll_run_line"
    PAYSLIP = "pay_payslip"
    TAXCONFIGURATION = "pay_tax_configuration"
    STATUTORYCONTRIBUTION = "pay_statutory_contribution"
    BONUS = "pay_bonus"
    REIMBURSEMENT = "pay_reimbursement"
    LOAN = "pay_loan"
    LOANINSTALLMENT = "pay_loan_installment"
    PAYROLLADJUSTMENT = "pay_payroll_adjustment"
    PAYROLLPOSTING = "pay_payroll_posting"
    PAYROLLSUMMARY = "pay_payroll_summary"
