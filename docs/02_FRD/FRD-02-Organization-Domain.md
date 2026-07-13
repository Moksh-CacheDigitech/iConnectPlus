# FRD-02 ORGANIZATION DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-01 Foundation Domain](./FRD-01-Foundation-Domain.md)
- Downstream dependency: [FRD-03 Master Data Domain](./FRD-03-Master-Data-Domain.md)

## 1. PURPOSE

Organization Domain ERP ki legal, operational aur reporting hierarchy define karega.

Ye domain define karega:

```
Tenant
↓
Company
↓
Branch
↓
Business Unit
↓
Department
↓
Cost Center
↓
Profit Center
```

ERP ke saare modules isi structure ko reference karenge.

## 2. BUSINESS OBJECTIVES

System shall:

- Support Multi-Tenant Architecture
- Support Multi-Company Operations
- Support Multi-Branch Operations
- Support Multi-Department Operations
- Support Cost Allocation
- Support Profitability Analysis
- Support Organizational Reporting

## 3. ORGANIZATION HIERARCHY

### Level 1

Tenant

Example:

Tenant: ABC Group

### Level 2

Company

Examples:

- ABC India Pvt Ltd
- ABC UAE LLC

### Level 3

Branch

Examples:

- Delhi
- Mumbai
- Bangalore
- Dubai

### Level 4

Business Unit

Examples:

- Manufacturing
- Retail
- Services

### Level 5

Department

Examples:

- Finance
- HR
- Sales
- Operations

### Level 6

Cost Center

Examples:

- Sales Delhi
- HR Corporate
- Production Unit 1

### Level 7

Profit Center

Examples:

- Retail Division
- Manufacturing Division

## 4. SCREEN INVENTORY

- Company List
- Company Create
- Company Details
- Branch List
- Branch Create
- Branch Details
- Business Unit List
- Business Unit Create
- Department List
- Department Create
- Cost Center List
- Cost Center Create
- Profit Center List
- Profit Center Create
- Organization Tree View

## 5. COMPANY MANAGEMENT

### Company Create Screen

#### Fields

| Field | Mandatory |
|---|---|
| Company Name | Yes |
| Company Code | Yes |
| Legal Name | Yes |
| Registration Number | Yes |
| Tax Number | Yes |
| Country | Yes |
| Base Currency | Yes |
| Timezone | Yes |
| Status | Yes |

#### Validation Rules

Company Code

Must be:

- Unique Across Tenant

Tax Number

Must be:

- Unique Per Country

#### Status Values

- Active
- Inactive
- Archived

## 6. BRANCH MANAGEMENT

### Branch Create

#### Fields

| Field | Mandatory |
|---|---|
| Company | Yes |
| Branch Name | Yes |
| Branch Code | Yes |
| Address | Yes |
| Country | Yes |
| State | Yes |
| City | Yes |
| Status | Yes |

#### Business Rules

Every branch must belong to:

- One Company

## 7. BUSINESS UNIT MANAGEMENT

### Fields

| Field |
|---|
| Business Unit Name |
| Business Unit Code |
| Description |
| Company |

### Examples

- Retail
- Manufacturing
- Services
- Wholesale

## 8. DEPARTMENT MANAGEMENT

### Fields

| Field |
|---|
| Department Name |
| Department Code |
| Department Head |
| Company |
| Branch |

### Examples

- Finance
- Human Resources
- Sales
- Operations
- IT

## 9. COST CENTER MANAGEMENT

### Purpose

Track expenses and budgets.

### Fields

| Field |
|---|
| Cost Center Name |
| Cost Center Code |
| Department |
| Branch |
| Manager |

### Referenced By

- Finance
- Payroll
- Projects
- Procurement

## 10. PROFIT CENTER MANAGEMENT

### Purpose

Track profitability.

### Fields

| Field |
|---|
| Profit Center Name |
| Profit Center Code |
| Business Unit |
| Branch |

### Referenced By

- Finance
- Sales
- Projects

## 11. ORGANIZATION TREE VIEW

### Purpose

Visual hierarchy management.

Example:

```
ABC Group
│
├── ABC India
│   ├── Delhi
│   │   ├── Finance
│   │   ├── HR
│   │
│   ├── Mumbai
│
├── ABC UAE
│   ├── Dubai
```

## 12. DATA OWNERSHIP RULES

Every business record shall contain:

- tenant_id
- company_id
- branch_id
- created_by
- updated_by

Mandatory.

## 13. PERMISSION MODEL

### Super Admin

Full Access

### Company Admin

Access:

- Own Company Only

### Branch Admin

Access:

- Own Branch Only

### Department Manager

Access:

- Own Department Only

## 14. WORKFLOWS

### Company Creation Workflow

```
Draft
↓
Review
↓
Approved
↓
Active
```

### Branch Creation Workflow

```
Draft
↓
Approval
↓
Active
```

## 15. NOTIFICATIONS

Events:

- Company Created
- Branch Created
- Department Updated
- Cost Center Created

Channels:

- Email
- In-App

## 16. AUDIT REQUIREMENTS

Track:

- Create
- Update
- Delete
- Activate
- Deactivate

For:

- Companies
- Branches
- Departments
- Cost Centers
- Profit Centers

## 17. DATABASE TABLES

- tenants
- companies
- branches
- business_units
- departments
- cost_centers
- profit_centers
- organization_settings

## 18. KEY RELATIONSHIPS

```
Tenant
1 → N Companies

Company
1 → N Branches

Branch
1 → N Departments

Department
1 → N Cost Centers

Business Unit
1 → N Profit Centers
```

## 19. API SPECIFICATIONS

### Company APIs

```
GET /api/v1/companies

POST /api/v1/companies

PUT /api/v1/companies/{id}

DELETE /api/v1/companies/{id}
```

### Branch APIs

```
GET /api/v1/branches

POST /api/v1/branches

PUT /api/v1/branches/{id}
```

### Department APIs

```
GET /api/v1/departments

POST /api/v1/departments

PUT /api/v1/departments/{id}
```

## 20. REPORTS

### Organization Reports

- Company Report
- Branch Report
- Department Report
- Cost Center Report
- Profit Center Report

## 21. ACCEPTANCE CRITERIA

✅ Multi-company works

✅ Multi-branch works

✅ Organization hierarchy enforced

✅ Data isolation enforced

✅ Permission scope enforced

✅ Audit logs generated

✅ Reports generated successfully

## 22. UAT SCENARIOS

### UAT-001

Create Company

Expected:

Company created successfully

### UAT-002

Create Branch

Expected:

Branch linked to company

### UAT-003

Branch Admin accesses another branch

Expected:

Access Denied

### UAT-004

Organization Tree loads

Expected:

Hierarchy displayed correctly

## Architect Review

FRD-02 Organization Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
Finance
HR
CRM
Sales
Inventory
```
