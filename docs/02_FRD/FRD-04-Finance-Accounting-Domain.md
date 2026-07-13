# FRD-04 FINANCE & ACCOUNTING DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-03 Master Data Domain](./FRD-03-Master-Data-Domain.md)
- Downstream dependencies: [FRD-06 Sales Domain](./FRD-06-Sales-Domain.md), [FRD-07 Procurement Domain](./FRD-07-Procurement-Domain.md), [FRD-10 Payroll Domain](./FRD-10-Payroll-Domain.md), [FRD-12 Asset Management Domain](./FRD-12-Asset-Management-Domain.md), [FRD-11 Project Management Domain](./FRD-11-Project-Management-Domain.md)

## 1. PURPOSE

Finance Domain organization ke saare financial transactions ko manage karega.

### Core Objectives

- Financial Control
- Financial Reporting
- Compliance
- Budget Control
- Profitability Analysis
- Tax Management

## 2. MODULES COVERED

- Chart of Accounts
- General Ledger
- Journal Entries
- Accounts Payable
- Accounts Receivable
- Budget Management
- Cost Center Accounting
- Profit Center Accounting
- Bank Reconciliation
- Tax Engine
- Financial Reporting

## 3. FINANCIAL ARCHITECTURE

### Principle

Golden Rule:

Every Financial Transaction

Must Create

Double Entry Accounting

### Example

Sales Invoice

- Accounts Receivable Dr
- Sales Revenue Cr

Purchase Invoice

- Expense Dr
- Accounts Payable Cr

## 4. CHART OF ACCOUNTS (COA)

### Purpose

Central account structure.

### Account Types

- Assets
- Liabilities
- Equity
- Revenue
- Expenses

### Account Create Fields

| Field | Mandatory |
|---|---|
| Account Code | Yes |
| Account Name | Yes |
| Account Type | Yes |
| Parent Account | No |
| Cost Center Enabled | No |
| Profit Center Enabled | No |
| Status | Yes |

### Account Code Example

- 1000 Assets
- 2000 Liabilities
- 3000 Equity
- 4000 Revenue
- 5000 Expenses

## 5. GENERAL LEDGER

### Purpose

Central accounting book.

### Features

- Ledger Posting
- Ledger Inquiry
- Ledger Adjustments
- Period Closing

### Business Rule

No transaction directly modifies GL.

All entries come from:

- Journal Entries
- Sales
- Purchases
- Payroll
- Assets

## 6. JOURNAL ENTRIES

### Entry Types

- Manual
- System Generated
- Adjustment
- Reversal

### Journal Fields

| Field |
|---|
| Journal Number |
| Date |
| Description |
| Debit Account |
| Credit Account |
| Amount |
| Currency |

### Validation

Rule:

Total Debit

Must Equal

Total Credit

## 7. ACCOUNTS RECEIVABLE (AR)

### Purpose

Track customer dues.

### Sources

- Sales Invoices
- Debit Notes

### Features

- Customer Aging
- Payment Tracking
- Credit Control
- Collections

### Aging Buckets

- 0-30
- 31-60
- 61-90
- 90+

## 8. ACCOUNTS PAYABLE (AP)

### Purpose

Track vendor liabilities.

### Sources

- Purchase Invoices
- Credit Notes

### Features

- Vendor Aging
- Payment Scheduling
- Payment Approvals

## 9. COST CENTER ACCOUNTING

### Purpose

Track departmental costs.

Examples:

- Sales Delhi
- HR Corporate
- Production Unit

### Referenced By

- Payroll
- Projects
- Procurement
- Expenses

## 10. PROFIT CENTER ACCOUNTING

### Purpose

Track profitability.

Examples:

- Retail Business
- Manufacturing Division
- Services Division

### Reports

- Profitability Report
- Revenue Analysis

## 11. BUDGET MANAGEMENT

### Budget Types

- Annual
- Quarterly
- Monthly

### Budget Fields

| Field |
|---|
| Budget Name |
| Cost Center |
| Amount |
| Fiscal Year |

### Controls

System shall:

- Warn
- Or
- Block

Budget Exceeding Transactions

## 12. TAX ENGINE

### Purpose

Central tax processing.

### Supported Taxes

- GST
- VAT
- TDS
- Service Tax

### Features

- Tax Rules
- Tax Calculation
- Tax Reports

### Tax Configuration

| Field |
|---|
| Tax Code |
| Rate |
| Effective Date |

## 13. BANK RECONCILIATION

### Purpose

Match ERP and Bank.

### Inputs

- Bank Statement
- ERP Transactions

### Outputs

- Matched Entries
- Unmatched Entries

## 14. FISCAL YEAR MANAGEMENT

### Fields

| Field |
|---|
| Fiscal Year |
| Start Date |
| End Date |
| Status |

### States

- Open
- Closed
- Archived

## 15. PERIOD CLOSING

### Monthly Closing

Checklist:

- AR Closed
- AP Closed
- Inventory Closed
- Payroll Closed

### Closing Rule

Closed period:

Cannot Be Edited

## 16. SCREEN INVENTORY

- Chart Of Accounts
- GL Inquiry
- Journal Entry
- Journal Approval
- AR Dashboard
- AP Dashboard
- Budget Dashboard
- Tax Dashboard
- Bank Reconciliation
- Financial Reports

## 17. APPROVAL WORKFLOWS

### Journal Approval

```
Draft
Submitted
Finance Manager
Approved
```

### Budget Approval

```
Draft
Department Head
Finance
Approved
```

### Vendor Payment

```
Finance Executive
Finance Manager
CFO
Approved
```

## 18. NOTIFICATIONS

Events

- Journal Approved
- Budget Approved
- Payment Due
- Payment Completed
- Fiscal Period Closing

Channels

- Email
- In-App
- SMS

## 19. AUDIT REQUIREMENTS

Track:

- Journal Changes
- Budget Changes
- Tax Changes
- Payment Approvals
- Period Closings

Retention:

7 Years

## 20. DATABASE TABLES

- chart_of_accounts
- journal_entries
- journal_lines
- general_ledger
- accounts_receivable
- accounts_payable
- budgets
- cost_centers
- profit_centers
- tax_rules
- bank_accounts
- bank_reconciliation
- fiscal_years
- period_closings

## 21. KEY RELATIONSHIPS

```
Chart Of Accounts
1:N Journal Entries

Journal Entries
1:N GL Entries

Customer
1:N Accounts Receivable

Vendor
1:N Accounts Payable

Cost Center
1:N Budgets
```

## 22. API SPECIFICATIONS

### Journal APIs

```
GET /api/v1/journals

POST /api/v1/journals

PUT /api/v1/journals/{id}
```

### GL APIs

```
GET /api/v1/gl

GET /api/v1/gl/trial-balance
```

### AR APIs

```
GET /api/v1/ar

POST /api/v1/ar/payment
```

### AP APIs

```
GET /api/v1/ap

POST /api/v1/ap/payment
```

## 23. REPORTS

### Financial Reports

- Trial Balance
- Balance Sheet
- Profit & Loss
- Cash Flow Statement

### AR Reports

- Customer Aging
- Outstanding Invoices

### AP Reports

- Vendor Aging
- Payment Forecast

### Budget Reports

- Budget vs Actual

### Tax Reports

- GST Report
- VAT Report
- TDS Report

## 24. ACCEPTANCE CRITERIA

✅ Double Entry Accounting enforced

✅ Journal Approval Workflow works

✅ AR Aging correct

✅ AP Aging correct

✅ Budget Controls work

✅ Tax Calculations accurate

✅ Bank Reconciliation functional

✅ Financial Reports generated

## 25. UAT SCENARIOS

### UAT-001

Create Journal Entry

Expected:

Debit = Credit

### UAT-002

Post Sales Invoice

Expected:

AR Created

GL Posted

### UAT-003

Budget Exceeded

Expected:

Warning or Block Triggered

### UAT-004

Close Fiscal Period

Expected:

Further Posting Blocked

## ARCHITECT REVIEW

FRD-04 Finance Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
Finance
↓
Sales
Procurement
Payroll
Assets
Projects
```
