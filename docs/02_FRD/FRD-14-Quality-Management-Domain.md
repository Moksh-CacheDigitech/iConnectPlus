# FRD-14 QUALITY MANAGEMENT DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependencies: [FRD-07 Procurement Domain](./FRD-07-Procurement-Domain.md), [FRD-13 Manufacturing Domain](./FRD-13-Manufacturing-Domain.md)
- Downstream dependency: [FRD-08 Inventory & Warehouse Domain](./FRD-08-Inventory-Warehouse-Domain.md)

## 1. PURPOSE

Quality Management Domain product aur process quality ensure karega.

### Business Objectives

- Defect Prevention
- Process Standardization
- Regulatory Compliance
- Product Quality Assurance
- Customer Satisfaction
- Continuous Improvement

## 2. MODULES COVERED

- Quality Planning
- Incoming Quality Inspection
- In-Process Quality Inspection
- Final Quality Inspection
- Quality Control (QC)
- Quality Assurance (QA)
- Non-Conformance Management (NCR)
- CAPA Management
- Quality Audits
- Compliance Management
- Customer Quality Complaints

## 3. QUALITY LIFECYCLE

```
Quality Plan
↓
Incoming Inspection
↓
In Process Inspection
↓
Final Inspection
↓
Release
↓
Customer Feedback
↓
Corrective Action
```

## 4. QUALITY PLANNING

### Purpose

Define quality standards.

### Fields

| Field | Mandatory |
|---|---|
| Plan Code | Yes |
| Plan Name | Yes |
| Product Category | Yes |
| Inspection Type | Yes |
| Status | Yes |

### Inspection Types

- Incoming
- In Process
- Final
- Customer Return

## 5. INCOMING QUALITY INSPECTION

### Purpose

Inspect purchased materials.

### Trigger

Goods Receipt Note (GRN)

### Inspection Result

- Accepted
- Rejected
- Conditional Acceptance

### Business Rule

Rejected Material:

Cannot Enter Production

## 6. IN-PROCESS QUALITY INSPECTION

### Purpose

Check production quality during manufacturing.

### Inspection Points

- Operation 1
- Operation 2
- Operation 3

### Data Captured

| Field |
|---|
| Work Order |
| Operation |
| Inspector |
| Result |

## 7. FINAL QUALITY INSPECTION

### Purpose

Inspect finished goods.

### Outcomes

- Approved
- Rejected
- Rework Required

### Business Rule

Only approved products can enter finished goods inventory.

## 8. QUALITY CHECKLIST MANAGEMENT

### Purpose

Standardize inspections.

### Checklist Types

- Product Quality
- Process Quality
- Safety Quality
- Compliance Quality

### Example

- Dimension Check
- Weight Check
- Packaging Check
- Label Check

## 9. NON-CONFORMANCE MANAGEMENT (NCR)

### Purpose

Track defects.

### NCR Fields

| Field |
|---|
| NCR Number |
| Source |
| Severity |
| Description |
| Status |

### Severity Levels

- Minor
- Major
- Critical

### NCR Number

```
NCR-2026-000001
```

## 10. CORRECTIVE & PREVENTIVE ACTION (CAPA)

### Purpose

Prevent recurring issues.

### CAPA Fields

| Field |
|---|
| CAPA Number |
| NCR Reference |
| Root Cause |
| Corrective Action |
| Preventive Action |

### Workflow

```
Issue
↓
Root Cause Analysis
↓
Corrective Action
↓
Verification
↓
Closure
```

## 11. QUALITY AUDIT MANAGEMENT

### Purpose

Internal quality reviews.

### Audit Types

- Internal Audit
- Supplier Audit
- Process Audit
- Compliance Audit

### Audit Status

- Planned
- In Progress
- Completed
- Closed

## 12. COMPLIANCE MANAGEMENT

### Purpose

Meet regulatory requirements.

### Standards

- ISO 9001
- ISO 27001
- ISO 14001
- FDA
- GMP

### Features

- Compliance Register
- Compliance Tracking
- Evidence Repository

## 13. CUSTOMER QUALITY COMPLAINTS

### Purpose

Track customer-reported quality issues.

### Complaint Types

- Defective Product
- Packaging Issue
- Performance Issue
- Wrong Product

### Workflow

```
Complaint
↓
Investigation
↓
NCR
↓
CAPA
↓
Closure
```

## 14. QUALITY SCORE MANAGEMENT

### Purpose

Measure quality performance.

### KPIs

- First Pass Yield
- Defect Rate
- Rework Rate
- Customer Complaint Rate
- Supplier Quality Score

## 15. SCREEN INVENTORY

- Quality Dashboard
- Inspection Dashboard
- Incoming Inspection
- In Process Inspection
- Final Inspection
- NCR Dashboard
- CAPA Dashboard
- Audit Dashboard
- Compliance Dashboard
- Quality Reports

## 16. APPROVAL WORKFLOWS

### NCR Approval

```
Inspector
↓
Quality Manager
↓
Approved
```

### CAPA Approval

```
Quality Engineer
↓
Quality Manager
↓
Approved
```

### Audit Closure

```
Auditor
↓
Quality Head
↓
Closed
```

## 17. NOTIFICATIONS

Events

- Inspection Failed
- NCR Created
- CAPA Assigned
- Audit Due
- Compliance Expiry

Channels

- Email
- In-App
- WhatsApp

## 18. AUDIT REQUIREMENTS

Track:

- Inspection Results
- Checklist Changes
- NCR Updates
- CAPA Updates
- Audit Findings
- Compliance Records

## 19. DATABASE TABLES

- quality_plans
- quality_checklists
- incoming_inspections
- inprocess_inspections
- final_inspections
- ncr_records
- capa_records
- quality_audits
- audit_findings
- compliance_register
- customer_complaints

## 20. KEY RELATIONSHIPS

```
GRN
1:N Incoming Inspections

Work Order
1:N In Process Inspections

Finished Goods
1:N Final Inspections

NCR
1:N CAPA Records

Audit
1:N Findings
```

## 21. API SPECIFICATIONS

### Inspection APIs

```
GET /api/v1/inspections

POST /api/v1/inspections
```

### NCR APIs

```
GET /api/v1/ncrs

POST /api/v1/ncrs

PUT /api/v1/ncrs/{id}
```

### CAPA APIs

```
GET /api/v1/capas

POST /api/v1/capas
```

## 22. REPORTS

### Quality Reports

- Incoming Inspection Report
- Production Quality Report
- NCR Report
- CAPA Report
- Supplier Quality Report
- Customer Complaint Report
- Audit Findings Report
- Compliance Status Report

## 23. ACCEPTANCE CRITERIA

✅ Incoming inspections work

✅ Production inspections work

✅ NCR workflow works

✅ CAPA workflow works

✅ Audit management works

✅ Compliance tracking works

✅ Customer complaints tracked

✅ Quality KPIs generated

## 24. UAT SCENARIOS

### UAT-001

Inspect Incoming Material

Expected:

Inspection Result Recorded

### UAT-002

Create NCR

Expected:

NCR Created Successfully

### UAT-003

Create CAPA

Expected:

Corrective Action Assigned

### UAT-004

Conduct Audit

Expected:

Findings Recorded

### UAT-005

Process Customer Complaint

Expected:

Complaint Closed Successfully

## ARCHITECT REVIEW

FRD-14 Quality Management Domain is now locked.

### Dependency Chain

```
Procurement
↓
Quality
↓
Manufacturing
↓
Inventory
↓
Customer
```

### Critical Observation

Quality module now supports:

- Supplier Quality Control
- Production Quality Control
- Finished Goods Quality
- NCR Management
- CAPA Management
- Audit & Compliance
- Customer Complaint Resolution
