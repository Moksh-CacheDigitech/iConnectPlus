# FRD-10 PAYROLL DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-09 HR Domain](./FRD-09-HR-Domain.md)
- Downstream dependency: [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md)

## 1. PURPOSE

Payroll Domain employee compensation lifecycle manage karega.

### Business Objectives

- Automated Payroll Processing
- Accurate Salary Computation
- Tax Compliance
- Employee Self-Service
- Finance Integration
- Statutory Compliance

## 2. MODULES COVERED

- Salary Structures
- Payroll Components
- Payroll Processing
- Allowances
- Deductions
- Loans & Advances
- Reimbursements
- Tax Management
- Payslip Generation
- Payroll Accounting
- Bank Transfer Processing

## 3. PAYROLL LIFECYCLE

```
Employee
↓
Attendance
↓
Leave Validation
↓
Payroll Processing
↓
Review
↓
Approval
↓
Payslip Generation
↓
Finance Posting
↓
Bank Transfer
```

## 4. SALARY STRUCTURE MANAGEMENT

### Purpose

Define employee compensation.

### Salary Structure Fields

| Field | Mandatory |
|---|---|
| Structure Code | Yes |
| Structure Name | Yes |
| Effective Date | Yes |
| Status | Yes |

### Structure Code

```
SAL-000001
```

### Components

- Basic Salary
- HRA
- Special Allowance
- Bonus
- Overtime
- Employer Contributions

## 5. PAYROLL COMPONENTS

### Earnings

- Basic
- HRA
- Medical
- Conveyance
- Special Allowance
- Bonus
- Incentive
- Overtime

### Deductions

- Tax
- Provident Fund
- ESI
- Professional Tax
- Loan Recovery
- Advance Recovery
- Other Deductions

## 6. PAYROLL PERIOD MANAGEMENT

### Fields

| Field |
|---|
| Payroll Month |
| Payroll Year |
| Start Date |
| End Date |
| Status |

### Status

- Open
- Processing
- Approved
- Closed

## 7. PAYROLL PROCESSING

### Purpose

Generate payroll.

### Inputs

- Employee Master
- Attendance
- Leaves
- Salary Structure
- Loans
- Reimbursements

### Processing Formula

```
Gross Salary
-
Deductions
=
Net Salary
```

## 8. ALLOWANCE MANAGEMENT

### Types

- Fixed
- Variable
- Percentage Based

### Examples

- HRA
- Travel Allowance
- Meal Allowance
- Project Allowance

## 9. DEDUCTION MANAGEMENT

### Types

- Statutory
- Voluntary
- Recovery

### Examples

- PF
- ESI
- Professional Tax
- Loan Recovery

## 10. LOANS & ADVANCES

### Purpose

Track employee liabilities.

### Loan Fields

| Field |
|---|
| Employee |
| Loan Type |
| Amount |
| EMI |
| Start Date |
| End Date |

### Loan Types

- Personal Loan
- Salary Advance
- Emergency Advance

## 11. REIMBURSEMENT MANAGEMENT

### Purpose

Employee expense reimbursement.

### Types

- Travel
- Internet
- Medical
- Training
- Mobile

### Workflow

```
Employee
↓
Manager
↓
Finance
↓
Approved
```

## 12. TAX MANAGEMENT

### Purpose

Payroll tax compliance.

### Supported Taxes

- Income Tax
- Professional Tax
- PF
- ESI

### Features

- Tax Slabs
- Tax Declaration
- Tax Projection
- Annual Tax Calculation

## 13. PAYSLIP GENERATION

### Purpose

Generate employee salary statement.

### Payslip Fields

| Field |
|---|
| Employee |
| Payroll Period |
| Gross Salary |
| Total Deductions |
| Net Salary |

### Payslip Number

```
PS-2026-000001
```

### Delivery

- ESS Portal
- Email

## 14. BANK TRANSFER PROCESSING

### Purpose

Salary disbursement.

### Payment Modes

- Bank Transfer
- Cheque
- Cash

### Output

Bank Payment File

## 15. PAYROLL ACCOUNTING

### Purpose

Integrate with Finance.

### Accounting Entry

Payroll Posting:

- Salary Expense Dr
- Payroll Liability Cr

Salary Payment:

- Payroll Liability Dr
- Bank Cr

## 16. SCREEN INVENTORY

- Payroll Dashboard
- Salary Structure Dashboard
- Payroll Processing Dashboard
- Loan Dashboard
- Reimbursement Dashboard
- Tax Dashboard
- Payslip Dashboard
- Bank Transfer Dashboard

## 17. APPROVAL WORKFLOWS

### Payroll Approval

```
HR Executive
↓
HR Manager
↓
Finance Manager
↓
Approved
```

### Loan Approval

```
Employee
↓
Manager
↓
HR
↓
Approved
```

### Reimbursement Approval

```
Employee
↓
Manager
↓
Finance
↓
Approved
```

## 18. NOTIFICATIONS

Events

- Payroll Processed
- Payslip Generated
- Loan Approved
- Reimbursement Approved
- Salary Paid

Channels

- Email
- In-App
- WhatsApp

## 19. AUDIT REQUIREMENTS

Track:

- Payroll Runs
- Salary Changes
- Tax Changes
- Loan Updates
- Reimbursement Approvals
- Payslip Generation

## 20. DATABASE TABLES

- salary_structures
- salary_components
- payroll_periods
- payroll_runs
- payroll_details
- employee_loans
- loan_repayments
- reimbursements
- tax_slabs
- tax_declarations
- payslips
- bank_transfers

## 21. KEY RELATIONSHIPS

```
Employee
1:N Payslips

Employee
1:N Loans

Employee
1:N Reimbursements

Payroll Run
1:N Payroll Details

Payroll Detail
1:1 Payslip
```

## 22. API SPECIFICATIONS

### Payroll APIs

```
GET /api/v1/payroll

POST /api/v1/payroll/process

POST /api/v1/payroll/approve
```

### Payslip APIs

```
GET /api/v1/payslips

GET /api/v1/payslips/{id}
```

### Loan APIs

```
GET /api/v1/loans

POST /api/v1/loans
```

### Reimbursement APIs

```
GET /api/v1/reimbursements

POST /api/v1/reimbursements
```

## 23. REPORTS

### Payroll Reports

- Payroll Summary Report
- Salary Register
- Payslip Report
- Loan Report
- Reimbursement Report
- Tax Report
- Bank Transfer Report
- Cost Center Payroll Report

## 24. ACCEPTANCE CRITERIA

✅ Payroll processed correctly

✅ Attendance integrated correctly

✅ Leave deductions calculated correctly

✅ Tax calculations accurate

✅ Payslips generated

✅ Finance posting completed

✅ Bank transfer file generated

✅ Audit logs maintained

## 25. UAT SCENARIOS

### UAT-001

Run Payroll

Expected:

Net Salary Calculated Correctly

### UAT-002

Generate Payslip

Expected:

Payslip Available In ESS

### UAT-003

Approve Loan

Expected:

Loan Schedule Created

### UAT-004

Approve Reimbursement

Expected:

Amount Included In Payroll

### UAT-005

Post Payroll To Finance

Expected:

Journal Entry Created

## ARCHITECT REVIEW

FRD-10 Payroll Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
HR
↓
Payroll
↓
Finance
```

### Critical Observation

Payroll Domain now supports:

- Salary Structures
- Payroll Processing
- Tax Compliance
- Loans & Advances
- Reimbursements
- Payslip Management
- Finance Integration
