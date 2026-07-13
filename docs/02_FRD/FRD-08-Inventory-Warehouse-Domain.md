# FRD-08 INVENTORY & WAREHOUSE DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependency: [FRD-07 Procurement Domain](./FRD-07-Procurement-Domain.md)
- Downstream dependencies: [FRD-13 Manufacturing Domain](./FRD-13-Manufacturing-Domain.md), [FRD-06 Sales Domain](./FRD-06-Sales-Domain.md), [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md)
- Related: [FRD-15 Supply Chain Management Domain](./FRD-15-Supply-Chain-Management-Domain.md)

## 1. PURPOSE

Inventory Domain organization ke stock aur warehouse operations ko manage karega.

### Business Objectives

- Real-Time Inventory Visibility
- Warehouse Optimization
- Stock Accuracy
- Traceability
- Inventory Valuation
- Stock Movement Control

## 2. MODULES COVERED

- Inventory Management
- Warehouse Management
- Bin Management
- Stock Movements
- Stock Transfers
- Stock Adjustments
- Batch Tracking
- Serial Number Tracking
- Barcode Management
- Cycle Counting
- Stock Valuation

## 3. INVENTORY LIFECYCLE

```
Purchase
↓
Goods Receipt
↓
Warehouse Storage
↓
Stock Movement
↓
Issue / Consumption
↓
Transfer
↓
Sale
↓
Inventory Valuation
```

## 4. INVENTORY MASTER

### Purpose

Central stock repository.

### Inventory Fields

| Field | Mandatory |
|---|---|
| Product | Yes |
| Warehouse | Yes |
| UOM | Yes |
| Available Qty | Yes |
| Reserved Qty | Yes |
| Status | Yes |

### Formula

Available Stock:

On Hand

-

Reserved

## 5. WAREHOUSE MANAGEMENT

### Purpose

Manage physical storage locations.

### Warehouse Types

- Main Warehouse
- Regional Warehouse
- Distribution Center
- Store
- Transit Warehouse

### Warehouse Fields

| Field |
|---|
| Warehouse Code |
| Warehouse Name |
| Branch |
| Capacity |
| Manager |

## 6. BIN MANAGEMENT

### Purpose

Precise stock location management.

### Example

```
Warehouse
Aisle A
Rack 1
Shelf 2
Bin 10
```

### Bin Code Format

```
BIN-A01-R01-S02-10
```

## 7. STOCK MOVEMENTS

### Movement Types

- Receipt
- Issue
- Transfer
- Adjustment
- Return

### Stock Ledger

Every stock movement creates ledger entry.

### Fields

| Field |
|---|
| Product |
| Movement Type |
| Quantity |
| Warehouse |
| Date |

## 8. STOCK TRANSFERS

### Purpose

Move inventory between warehouses.

### Transfer Types

- Branch To Branch
- Warehouse To Warehouse
- Bin To Bin

### Workflow

```
Requested
↓
Approved
↓
In Transit
↓
Received
↓
Closed
```

## 9. STOCK ADJUSTMENTS

### Purpose

Correct inventory discrepancies.

### Reasons

- Damage
- Loss
- Shrinkage
- Counting Error
- Expiry

### Approval Required

Yes

## 10. BATCH TRACKING

### Purpose

Track inventory batches.

### Fields

| Field |
|---|
| Batch Number |
| Manufacturing Date |
| Expiry Date |
| Quantity |

### Batch Number Format

```
BATCH-2026-000001
```

## 11. SERIAL NUMBER TRACKING

### Purpose

Track unique items.

### Applicable For

- Laptops
- Servers
- Machines
- Equipment

### Serial Format

```
SN-2026-000001
```

## 12. BARCODE MANAGEMENT

### Purpose

Enable scanning.

### Barcode Types

- EAN
- UPC
- QR Code
- Code128

### Features

- Barcode Generation
- Barcode Printing
- Barcode Scanning

## 13. CYCLE COUNTING

### Purpose

Inventory verification.

### Count Types

- Daily
- Weekly
- Monthly
- Annual

### Count Results

- Match
- Shortage
- Excess

## 14. STOCK VALUATION

### Purpose

Calculate inventory value.

### Valuation Methods

- FIFO
- LIFO
- Weighted Average

### Recommended

FIFO

## 15. INVENTORY RESERVATION

### Purpose

Reserve stock for orders.

### Sources

- Sales Orders
- Production Orders
- Projects

### Rule

Reserved Stock:

Cannot Be Sold Again

## 16. SCREEN INVENTORY

- Inventory Dashboard
- Stock Ledger
- Warehouse Dashboard
- Bin Management
- Transfer Dashboard
- Adjustment Dashboard
- Batch Dashboard
- Serial Tracking Dashboard
- Cycle Count Dashboard
- Valuation Dashboard

## 17. APPROVAL WORKFLOWS

### Stock Transfer

```
Requester
↓
Warehouse Manager
↓
Approved
```

### Stock Adjustment

```
Warehouse Executive
↓
Warehouse Manager
↓
Finance Review
↓
Approved
```

### Cycle Count Variance

```
Counter
↓
Manager
↓
Approved
```

## 18. NOTIFICATIONS

Events

- Low Stock
- Transfer Approved
- Stock Adjustment
- Cycle Count Variance
- Batch Expiry Alert

Channels

- Email
- In-App
- WhatsApp

## 19. AUDIT REQUIREMENTS

Track:

- Stock Receipt
- Stock Issue
- Stock Transfer
- Stock Adjustment
- Cycle Count
- Valuation Changes

## 20. DATABASE TABLES

- inventory
- inventory_ledger
- warehouses
- warehouse_bins
- stock_transfers
- stock_transfer_items
- stock_adjustments
- stock_adjustment_items
- batches
- serial_numbers
- barcodes
- cycle_counts
- inventory_valuations

## 21. KEY RELATIONSHIPS

```
Warehouse
1:N Bins

Product
1:N Inventory

Inventory
1:N Ledger Entries

Inventory
1:N Batches

Inventory
1:N Serial Numbers

Transfer
1:N Transfer Items
```

## 22. API SPECIFICATIONS

### Inventory APIs

```
GET /api/v1/inventory

GET /api/v1/inventory/ledger
```

### Transfer APIs

```
GET /api/v1/transfers

POST /api/v1/transfers

PUT /api/v1/transfers/{id}
```

### Adjustment APIs

```
GET /api/v1/adjustments

POST /api/v1/adjustments
```

### Cycle Count APIs

```
GET /api/v1/cycle-counts

POST /api/v1/cycle-counts
```

## 23. REPORTS

### Inventory Reports

- Stock Summary Report
- Stock Ledger Report
- Inventory Aging Report
- Batch Expiry Report
- Serial Tracking Report
- Stock Transfer Report
- Stock Adjustment Report
- Inventory Valuation Report
- Cycle Count Variance Report

## 24. ACCEPTANCE CRITERIA

✅ Stock updates in real time

✅ Transfers work correctly

✅ Adjustments require approval

✅ Batch tracking works

✅ Serial tracking works

✅ Barcode scanning works

✅ Inventory valuation accurate

✅ Audit logs generated

## 25. UAT SCENARIOS

### UAT-001

Receive Goods

Expected:

Inventory Increased

### UAT-002

Transfer Stock

Expected:

Inventory Moved Successfully

### UAT-003

Perform Cycle Count

Expected:

Variance Calculated

### UAT-004

Reserve Stock For Sales Order

Expected:

Reserved Quantity Updated

### UAT-005

Generate Valuation Report

Expected:

Inventory Value Calculated Correctly

## ARCHITECT REVIEW

FRD-08 Inventory & Warehouse Domain is now locked.

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
Inventory
↓
Manufacturing
↓
Sales
↓
Finance
```

### Critical Observation

Inventory Domain now supports:

- Real-Time Stock Control
- Warehouse Operations
- Batch & Serial Traceability
- Inventory Valuation
- Stock Reservations
- Audit-Compliant Stock Ledger
