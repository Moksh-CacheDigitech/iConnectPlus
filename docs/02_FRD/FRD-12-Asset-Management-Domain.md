# FRD-12 ASSET MANAGEMENT DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-07 Procurement Domain](./FRD-07-Procurement-Domain.md)
- Downstream dependencies: [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md), [FRD-09 HR Domain](./FRD-09-HR-Domain.md)
- Related: [FRD-16 Service Management Domain](./FRD-16-Service-Management-Domain.md), [FRD-17 Helpdesk & Customer Support Domain](./FRD-17-Helpdesk-Customer-Support-Domain.md)

## 1. PURPOSE

Asset Management Domain organization ke physical aur digital assets ka complete lifecycle manage karega.

### Business Objectives

- Asset Visibility
- Asset Accountability
- Asset Maintenance
- Depreciation Tracking
- Asset Lifecycle Management
- Compliance & Audit Readiness

## 2. MODULES COVERED

- Asset Registration
- Asset Categorization
- Asset Allocation
- Asset Tracking
- Asset Maintenance
- Asset Depreciation
- Asset Transfer
- Asset Return
- Asset Disposal
- Asset Lifecycle Management

## 3. ASSET LIFECYCLE

```
Purchase
↓
Asset Registration
↓
Allocation
↓
Usage
↓
Maintenance
↓
Transfer
↓
Return
↓
Disposal
```

## 4. ASSET REGISTRATION

### Purpose

Register assets into ERP.

### Asset Fields

| Field | Mandatory |
|---|---|
| Asset Code | Yes |
| Asset Name | Yes |
| Asset Category | Yes |
| Asset Type | Yes |
| Purchase Date | Yes |
| Purchase Cost | Yes |
| Company | Yes |
| Branch | Yes |
| Status | Yes |

### Asset Code Format

```
AST-2026-000001
```

### Asset Categories

- IT Assets
- Furniture
- Vehicles
- Machinery
- Infrastructure
- Software Licenses

## 5. ASSET CATEGORIZATION

### Asset Types

- Fixed Asset
- Consumable Asset
- Digital Asset
- Leased Asset

### Purpose

Enable reporting and accounting classification.

## 6. ASSET ALLOCATION

### Purpose

Assign assets to employees, departments or locations.

### Allocation Types

- Employee
- Department
- Project
- Branch
- Warehouse

### Allocation Fields

| Field |
|---|
| Asset |
| Allocation Type |
| Allocated To |
| Allocation Date |
| Expected Return Date |

### Business Rule

One asset cannot be allocated to multiple employees simultaneously unless marked as shared.

## 7. ASSET TRACKING

### Purpose

Track asset ownership and location.

### Tracking Methods

- Barcode
- QR Code
- RFID
- Manual Tracking

### Trackable Data

- Current Owner
- Current Location
- Allocation History
- Status History

## 8. ASSET MAINTENANCE

### Purpose

Manage preventive and corrective maintenance.

### Maintenance Types

- Preventive
- Corrective
- Emergency
- Annual Service

### Maintenance Fields

| Field |
|---|
| Asset |
| Maintenance Type |
| Scheduled Date |
| Completion Date |
| Vendor |
| Cost |
| Status |

- Scheduled
- In Progress
- Completed
- Cancelled

## 9. ASSET DEPRECIATION

### Purpose

Calculate asset value reduction.

### Methods

- Straight Line
- Written Down Value
- Units Of Production

### Recommended

Straight Line

### Formula

```
Annual Depreciation
=
(Purchase Cost - Salvage Value)
/
Useful Life
```

### Finance Impact

Monthly depreciation posting:

- Depreciation Expense Dr
- Accumulated Depreciation Cr

## 10. ASSET TRANSFER

### Purpose

Move assets between entities.

### Transfer Types

- Employee To Employee
- Department To Department
- Branch To Branch
- Project To Project

### Workflow

```
Request
↓
Approval
↓
Transfer
↓
Confirmation
```

## 11. ASSET RETURN

### Purpose

Recover assets.

### Triggers

- Employee Resignation
- Project Completion
- Department Change
- Asset Replacement

### Validation

Asset must be returned before employee clearance.

## 12. ASSET DISPOSAL

### Purpose

Retire assets.

### Disposal Types

- Sale
- Scrap
- Donation
- Write-Off

### Approval Required

Mandatory.

### Finance Impact

- Remove Asset Value
- Calculate Gain/Loss

## 13. ASSET LIFECYCLE MANAGEMENT

### Asset States

- Registered
- Allocated
- In Use
- Under Maintenance
- Returned
- Disposed

### State Transitions

Controlled through workflow engine.

## 14. SCREEN INVENTORY

- Asset Dashboard
- Asset Register
- Asset Allocation Dashboard
- Asset Tracking Dashboard
- Maintenance Dashboard
- Depreciation Dashboard
- Transfer Dashboard
- Return Dashboard
- Disposal Dashboard
- Asset Lifecycle Dashboard

## 15. APPROVAL WORKFLOWS

### Asset Allocation

```
Asset Manager
↓
Department Head
↓
Approved
```

### Asset Transfer

```
Requester
↓
Asset Manager
↓
Approved
```

### Asset Disposal

```
Asset Manager
↓
Finance Manager
↓
CFO
↓
Approved
```

## 16. NOTIFICATIONS

Events

- Asset Allocated
- Asset Returned
- Maintenance Due
- Maintenance Completed
- Depreciation Run
- Asset Disposal Approved

Channels

- Email
- In-App
- WhatsApp

## 17. AUDIT REQUIREMENTS

Track:

- Asset Creation
- Asset Allocation
- Asset Transfer
- Maintenance Updates
- Depreciation Posting
- Disposal Approval

### Retention

7 Years Minimum

## 18. DATABASE TABLES

- assets
- asset_categories
- asset_allocations
- asset_transfers
- asset_returns
- asset_maintenance
- maintenance_vendors
- asset_depreciation
- asset_disposals
- asset_lifecycle_logs

## 19. KEY RELATIONSHIPS

```
Asset
1:N Allocations

Asset
1:N Maintenance Records

Asset
1:N Depreciation Entries

Asset
1:N Transfers

Employee
1:N Asset Allocations
```

## 20. API SPECIFICATIONS

### Asset APIs

```
GET /api/v1/assets

POST /api/v1/assets

PUT /api/v1/assets/{id}
```

### Allocation APIs

```
GET /api/v1/asset-allocations

POST /api/v1/asset-allocations
```

### Maintenance APIs

```
GET /api/v1/maintenance

POST /api/v1/maintenance
```

### Disposal APIs

```
GET /api/v1/disposals

POST /api/v1/disposals
```

## 21. REPORTS

### Asset Reports

- Asset Register Report
- Asset Allocation Report
- Asset Utilization Report
- Maintenance Cost Report
- Depreciation Report
- Asset Transfer Report
- Asset Disposal Report
- Asset Lifecycle Report

## 22. ACCEPTANCE CRITERIA

✅ Asset registration works

✅ Asset allocation works

✅ Asset transfer workflow works

✅ Maintenance schedules work

✅ Depreciation calculated correctly

✅ Asset return process works

✅ Disposal workflow works

✅ Finance postings generated

## 23. UAT SCENARIOS

### UAT-001

Register Asset

Expected:

Asset Created Successfully

### UAT-002

Allocate Asset

Expected:

Asset Assigned To Employee

### UAT-003

Run Depreciation

Expected:

Depreciation Entry Generated

### UAT-004

Transfer Asset

Expected:

Ownership Updated

### UAT-005

Dispose Asset

Expected:

Asset Status Changed To Disposed

## ARCHITECT REVIEW

FRD-12 Asset Management Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
Procurement
↓
Assets
↓
Finance
↓
HR
```

### Critical Observation

Asset Domain now supports:

- Complete Asset Lifecycle
- Employee Asset Tracking
- Preventive Maintenance
- Depreciation Accounting
- Asset Transfers
- Disposal Governance
- Audit Compliance
