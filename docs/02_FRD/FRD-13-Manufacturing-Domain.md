# FRD-13 MANUFACTURING DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-08 Inventory & Warehouse Domain](./FRD-08-Inventory-Warehouse-Domain.md)
- Downstream dependency: [FRD-14 Quality Management Domain](./FRD-14-Quality-Management-Domain.md)

## 1. PURPOSE

Manufacturing Domain raw materials ko finished goods mein convert karne ke complete production lifecycle ko manage karega.

### Business Objectives

- Production Planning
- Material Requirement Planning (MRP)
- Shop Floor Control
- Capacity Optimization
- Cost Control
- Quality Assurance
- Production Traceability

## 2. MODULES COVERED

- Bill Of Materials (BOM)
- Routing Management
- Production Planning
- Material Requirement Planning (MRP)
- Work Orders
- Capacity Planning
- Shop Floor Control
- Material Consumption
- Production Execution
- Finished Goods Receipt
- Scrap Management
- Rework Management
- Production Costing

## 3. MANUFACTURING LIFECYCLE

```
Demand
↓
Production Planning
↓
MRP
↓
Work Order
↓
Material Issue
↓
Production
↓
Quality Check
↓
Finished Goods Receipt
↓
Inventory
↓
Sales
```

## 4. BILL OF MATERIALS (BOM)

### Purpose

Define finished product structure.

### BOM Fields

| Field | Mandatory |
|---|---|
| BOM Number | Yes |
| Product | Yes |
| Revision | Yes |
| Effective Date | Yes |
| Status | Yes |

### BOM Number

```
BOM-2026-000001
```

### BOM Components

| Field |
|---|
| Raw Material |
| Quantity |
| UOM |
| Scrap % |
| Alternative Material |

### Example

```
Laptop

├── Motherboard
├── RAM
├── SSD
├── Battery
└── Screen
```

## 5. BOM VERSION CONTROL

### Purpose

Track engineering changes.

### Status

- Draft
- Active
- Obsolete

### Rule

Only one active BOM per product.

## 6. ROUTING MANAGEMENT

### Purpose

Define manufacturing operations.

### Example

```
Cutting
↓
Assembly
↓
Testing
↓
Packaging
```

### Routing Fields

| Field |
|---|
| Routing Code |
| Operation |
| Work Center |
| Standard Time |
| Setup Time |

## 7. WORK CENTER MANAGEMENT

### Purpose

Manage production resources.

### Work Center Types

- Machine
- Assembly Line
- Packaging Line
- Inspection Station

### Fields

| Field |
|---|
| Work Center Code |
| Capacity |
| Shift |
| Status |

## 8. PRODUCTION PLANNING

### Purpose

Create production schedules.

### Planning Inputs

- Sales Forecast
- Sales Orders
- Inventory Levels
- Production Capacity

### Outputs

- Production Plan
- Work Orders
- Material Requirements

## 9. MATERIAL REQUIREMENT PLANNING (MRP)

### Purpose

Calculate material requirements.

### Inputs

- Production Plan
- Current Inventory
- Open Purchase Orders
- BOM

### Outputs

- Material Shortages
- Purchase Requisitions
- Production Orders

### Formula

```
Required Material
=
Planned Production
×
BOM Quantity
```

## 10. WORK ORDER MANAGEMENT

### Purpose

Execute manufacturing jobs.

### Work Order Fields

| Field |
|---|
| Work Order Number |
| Product |
| Quantity |
| Planned Start |
| Planned End |
| Status |

### Work Order Number

```
WO-2026-000001
```

### Status

- Draft
- Released
- In Progress
- Completed
- Closed
- Cancelled

## 11. MATERIAL ISSUE

### Purpose

Issue raw materials to production.

### Inventory Impact

```
Raw Material Stock
↓
Consumed
```

### Validation

Material must exist in inventory.

## 12. PRODUCTION EXECUTION

### Purpose

Track actual production.

### Data Captured

- Produced Quantity
- Rejected Quantity
- Scrap Quantity
- Operator
- Machine

## 13. SHOP FLOOR CONTROL

### Purpose

Monitor production operations.

### Features

- Work Order Tracking
- Machine Status
- Operator Tracking
- Production Monitoring

### Machine Status

- Idle
- Running
- Maintenance
- Breakdown

## 14. CAPACITY PLANNING

### Purpose

Optimize production resources.

### Inputs

- Machine Capacity
- Labor Capacity
- Shift Capacity

### Outputs

- Utilization %
- Available Capacity
- Overload Alerts

## 15. FINISHED GOODS RECEIPT

### Purpose

Move production output into inventory.

### Inventory Impact

```
Finished Goods Stock
↑
Increase
```

### Trigger

Completed Work Order.

## 16. SCRAP MANAGEMENT

### Purpose

Track production waste.

### Scrap Types

- Material Scrap
- Process Scrap
- Damaged Goods

### Fields

| Field |
|---|
| Scrap Quantity |
| Reason |
| Cost Impact |

## 17. REWORK MANAGEMENT

### Purpose

Correct defective production.

### Rework Triggers

- Quality Failure
- Customer Return
- Production Error

### Workflow

```
Defect
↓
Inspection
↓
Rework Order
↓
Completion
```

## 18. PRODUCTION COSTING

### Purpose

Calculate manufacturing costs.

### Cost Components

- Material Cost
- Labor Cost
- Machine Cost
- Overhead Cost

### Formula

```
Production Cost
=
Material
+
Labor
+
Overheads
```

## 19. ACCOUNTING IMPACT

### Material Issue

- WIP Dr
- Raw Material Inventory Cr

### Finished Goods Receipt

- Finished Goods Inventory Dr
- WIP Cr

### Scrap

- Scrap Expense Dr
- Inventory Cr

## 20. SCREEN INVENTORY

- Manufacturing Dashboard
- BOM Management
- Routing Dashboard
- MRP Dashboard
- Production Plan Dashboard
- Work Order Dashboard
- Shop Floor Dashboard
- Capacity Dashboard
- Material Issue Dashboard
- Production Cost Dashboard
- Scrap Dashboard
- Rework Dashboard

## 21. APPROVAL WORKFLOWS

### BOM Approval

```
Engineer
↓
Production Manager
↓
Approved
```

### Production Plan Approval

```
Planner
↓
Production Head
↓
Approved
```

### Work Order Release

```
Production Manager
↓
Approved
```

### Scrap Approval

```
Supervisor
↓
Production Manager
↓
Finance
↓
Approved
```

## 22. NOTIFICATIONS

Events

- MRP Shortage Alert
- Work Order Released
- Production Completed
- Machine Breakdown
- Capacity Overload
- Scrap Exceeded Threshold

Channels

- Email
- In-App
- WhatsApp

## 23. AUDIT REQUIREMENTS

Track:

- BOM Changes
- Routing Changes
- Work Order Changes
- Material Issues
- Production Entries
- Scrap Entries
- Rework Orders

## 24. DATABASE TABLES

- boms
- bom_components
- routing_headers
- routing_operations
- work_centers
- production_plans
- mrp_runs
- mrp_requirements
- work_orders
- material_issues
- production_entries
- finished_goods_receipts
- scrap_records
- rework_orders
- production_costs

## 25. KEY RELATIONSHIPS

```
Product
1:N BOMs

BOM
1:N BOM Components

Product
1:N Work Orders

Work Order
1:N Material Issues

Work Order
1:N Production Entries

Work Order
1:N Scrap Records
```

## 26. API SPECIFICATIONS

### BOM APIs

```
GET /api/v1/boms

POST /api/v1/boms

PUT /api/v1/boms/{id}
```

### Work Order APIs

```
GET /api/v1/work-orders

POST /api/v1/work-orders

PUT /api/v1/work-orders/{id}
```

### MRP APIs

```
POST /api/v1/mrp/run

GET /api/v1/mrp/results
```

### Production APIs

```
POST /api/v1/production/entry

POST /api/v1/material-issue
```

## 27. REPORTS

### Manufacturing Reports

- BOM Report
- Production Plan Report
- MRP Shortage Report
- Work Order Report
- Capacity Utilization Report
- Production Cost Report
- Scrap Analysis Report
- Rework Analysis Report
- Machine Utilization Report

## 28. ACCEPTANCE CRITERIA

✅ BOM management works

✅ MRP calculates shortages correctly

✅ Work orders execute successfully

✅ Material consumption tracked

✅ Finished goods inventory updated

✅ Production costing calculated

✅ Scrap tracked accurately

✅ Finance postings generated

## 29. UAT SCENARIOS

### UAT-001

Create BOM

Expected:

BOM Saved Successfully

### UAT-002

Run MRP

Expected:

Material Shortages Generated

### UAT-003

Release Work Order

Expected:

Production Started

### UAT-004

Complete Production

Expected:

Finished Goods Added To Inventory

### UAT-005

Record Scrap

Expected:

Scrap Cost Captured

## ARCHITECT REVIEW

FRD-13 Manufacturing Domain is now locked.

### Critical Enterprise Gap Identified

Before moving further, Manufacturing ke baad FRD-14 Quality Management aana mandatory hai.

Reason:

```
Procurement
↓
Incoming Quality Check

Manufacturing
↓
In Process Quality Check

Finished Goods
↓
Final Quality Check

Customer
↓
Complaint Quality Check
```
