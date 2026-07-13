# FRD-03 MASTER DATA DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-02 Organization Domain](./FRD-02-Organization-Domain.md)
- Downstream dependencies: [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md), [FRD-05 CRM Domain](./FRD-05-CRM-Domain.md), [FRD-06 Sales Domain](./FRD-06-Sales-Domain.md), [FRD-07 Procurement Domain](./FRD-07-Procurement-Domain.md), [FRD-08 Inventory & Warehouse Domain](./FRD-08-Inventory-Warehouse-Domain.md), [FRD-13 Manufacturing Domain](./FRD-13-Manufacturing-Domain.md)

## 1. PURPOSE

Master Data Domain ERP ke core business entities ko manage karega.

Ye domain ensure karega:

- Single Source of Truth
- Standardized Data
- Data Reusability
- Cross Module Consistency
- Reporting Accuracy

## 2. MODULES COVERED

- Employee Master
- Customer Master
- Vendor Master
- Product Master
- Warehouse Master
- Asset Master
- Tax Master
- Currency Master
- UOM Master

## 3. MASTER DATA GOVERNANCE RULES

### Rule 1

Master Data centrally maintained hoga.

### Rule 2

Duplicate records allowed nahi honge.

### Rule 3

Every master record must have:

- tenant_id
- company_id
- status
- created_by
- created_at
- updated_by
- updated_at

### Rule 4

Soft Delete Only

Delete
=
Archive

Actual delete prohibited.

## 4. EMPLOYEE MASTER

### Purpose

Central employee repository.

### Referenced By:

- HR
- Payroll
- Projects
- Assets
- Helpdesk
- Workflow Engine

### Employee Create Fields

| Field | Mandatory |
|---|---|
| Employee Code | Yes |
| First Name | Yes |
| Last Name | Yes |
| Email | Yes |
| Mobile | Yes |
| Company | Yes |
| Branch | Yes |
| Department | Yes |
| Designation | Yes |
| Reporting Manager | No |
| Date of Joining | Yes |
| Status | Yes |

### Employee Status

- Draft
- Active
- On Leave
- Resigned
- Terminated

### Employee Code Format

```
EMP-000001
```

Auto Generated

## 5. CUSTOMER MASTER

### Purpose

Maintain all customers.

### Referenced By:

- CRM
- Sales
- Finance
- Helpdesk

### Fields

| Field | Mandatory |
|---|---|
| Customer Code | Yes |
| Customer Name | Yes |
| Customer Type | Yes |
| Tax Number | No |
| Email | No |
| Mobile | No |
| Billing Address | Yes |
| Shipping Address | No |
| Credit Limit | No |
| Status | Yes |

### Customer Types

- Individual
- Corporate
- Government

### Customer Code

```
CUS-000001
```

## 6. VENDOR MASTER

### Purpose

Supplier Management

### Referenced By:

- Procurement
- Inventory
- Finance

### Fields

| Field |
|---|
| Vendor Code |
| Vendor Name |
| Tax Number |
| Contact Person |
| Mobile |
| Email |
| Payment Terms |
| Status |

### Vendor Code

```
VEN-000001
```

## 7. PRODUCT MASTER

### Purpose

Central product catalog.

Most critical master.

### Referenced By:

- Sales
- Procurement
- Inventory
- Manufacturing
- Projects

### Fields

| Field |
|---|
| Product Code |
| Product Name |
| Category |
| UOM |
| Tax Category |
| Cost Price |
| Selling Price |
| Barcode |
| Status |

### Product Types

- Inventory Item
- Service
- Raw Material
- Finished Good
- Consumable

### Product Code

```
PRD-000001
```

## 8. WAREHOUSE MASTER

### Purpose

Manage storage locations.

### Referenced By:

- Inventory
- SCM
- Manufacturing

### Fields

| Field |
|---|
| Warehouse Code |
| Warehouse Name |
| Branch |
| Address |
| Capacity |
| Status |

### Warehouse Code

```
WH-000001
```

## 9. ASSET MASTER

### Purpose

Manage company assets.

### Referenced By:

- Asset Management
- Finance
- HR

### Fields

| Field |
|---|
| Asset Code |
| Asset Name |
| Asset Type |
| Purchase Date |
| Purchase Cost |
| Assigned Employee |
| Status |

### Asset Code

```
AST-000001
```

## 10. TAX MASTER

### Purpose

Central tax configuration.

### Referenced By:

- Sales
- Finance
- Procurement

### Tax Types

- GST
- VAT
- TDS
- Service Tax

### Fields

| Field |
|---|
| Tax Code |
| Tax Name |
| Tax Rate |
| Effective Date |
| Status |

## 11. CURRENCY MASTER

### Purpose

Multi-currency support.

### Fields

| Field |
|---|
| Currency Code |
| Currency Name |
| Symbol |
| Exchange Rate |
| Status |

### Examples

- INR
- USD
- EUR
- AED

## 12. UOM MASTER

### Purpose

Standard measurement units.

### Fields

| Field |
|---|
| UOM Code |
| UOM Name |
| Decimal Precision |
| Status |

### Examples

- KG
- LTR
- PCS
- BOX
- MTR

## 13. SCREEN INVENTORY

- Employee List
- Customer List
- Vendor List
- Product List
- Warehouse List
- Asset List
- Tax List
- Currency List
- UOM List
- Master Dashboard

## 14. DATA VALIDATION RULES

Email

Must be valid email format.

Mobile

Must be country specific.

Tax Number

Must be unique.

Product Code

Must be unique.

Employee Code

Must be unique.

Customer Code

Must be unique.

## 15. APPROVAL WORKFLOWS

### Employee Creation

```
Draft
↓
HR Review
↓
Approved
↓
Active
```

### Customer Creation

```
Draft
↓
Sales Review
↓
Approved
```

### Product Creation

```
Draft
↓
Inventory Review
↓
Finance Validation
↓
Approved
```

## 16. NOTIFICATIONS

Events

- Employee Created
- Customer Approved
- Vendor Approved
- Product Created
- Warehouse Created

Channels

- Email
- In-App

## 17. AUDIT REQUIREMENTS

Track:

- Create
- Update
- Archive
- Approve
- Reject

For every master record.

## 18. DATABASE TABLES

- employees
- customers
- vendors
- products
- warehouses
- assets
- taxes
- currencies
- uoms
- product_categories
- asset_categories

## 19. KEY RELATIONSHIPS

```
Company
1:N Employees

Company
1:N Customers

Company
1:N Vendors

Company
1:N Products

Branch
1:N Warehouses

Employee
1:N Assets
```

## 20. API SPECIFICATIONS

### Employee APIs

```
GET /api/v1/employees

POST /api/v1/employees

PUT /api/v1/employees/{id}
```

### Customer APIs

```
GET /api/v1/customers

POST /api/v1/customers

PUT /api/v1/customers/{id}
```

### Product APIs

```
GET /api/v1/products

POST /api/v1/products

PUT /api/v1/products/{id}
```

## 21. REPORTS

- Employee Master Report
- Customer Master Report
- Vendor Master Report
- Product Catalog Report
- Warehouse Report
- Asset Register Report

## 22. ACCEPTANCE CRITERIA

✅ Unique master records maintained

✅ Duplicate prevention works

✅ Approval workflows work

✅ Organization hierarchy enforced

✅ Audit logs generated

✅ Reports generated

## 23. UAT SCENARIOS

### UAT-001

Create Employee

Expected:

Employee Created Successfully

### UAT-002

Duplicate Customer Code

Expected:

Validation Error

### UAT-003

Product Approval Workflow

Expected:

Product becomes Active after Approval

### UAT-004

Warehouse linked to Branch

Expected:

Relationship saved correctly

## Architect Review

FRD-03 Master Data Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
Finance
CRM
Sales
Procurement
Inventory
Manufacturing
```
