# FRD-06 SALES DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Upstream dependencies: [FRD-05 CRM Domain](./FRD-05-CRM-Domain.md), [FRD-03 Master Data Domain](./FRD-03-Master-Data-Domain.md)
- Downstream dependency: [FRD-04 Finance & Accounting Domain](./FRD-04-Finance-Accounting-Domain.md)
- Integration dependency: [FRD-08 Inventory & Warehouse Domain](./FRD-08-Inventory-Warehouse-Domain.md)

## 1. PURPOSE

Sales Domain customer orders ko manage karega from quotation to payment collection.

### Business Objectives

- Sales Process Automation
- Revenue Tracking
- Customer Order Management
- Pricing Standardization
- Invoice Generation
- Payment Tracking

## 2. MODULES COVERED

- Quotation Management
- Sales Order Management
- Pricing Engine
- Contract Management
- Invoice Management
- Payment Tracking
- Returns Management
- Credit Notes
- Sales Analytics

## 3. SALES LIFECYCLE

```
Lead
↓
Opportunity
↓
Quotation
↓
Customer Approval
↓
Sales Order
↓
Delivery
↓
Invoice
↓
Payment
↓
Closed
```

## 4. QUOTATION MANAGEMENT

### Purpose

Customer proposal generation.

### Quotation Fields

| Field | Mandatory |
|---|---|
| Quotation Number | Yes |
| Customer | Yes |
| Opportunity | No |
| Quotation Date | Yes |
| Valid Until | Yes |
| Currency | Yes |
| Payment Terms | No |
| Total Amount | Yes |
| Status | Yes |

### Quotation Number Format

```
QT-2026-000001
```

### Quotation Status

- Draft
- Submitted
- Sent
- Accepted
- Rejected
- Expired

### Business Rules

Accepted quotation:

Can Create Sales Order

Rejected quotation:

Cannot Create Sales Order

## 5. QUOTATION ITEMS

### Fields

| Field |
|---|
| Product |
| Description |
| Quantity |
| UOM |
| Unit Price |
| Discount |
| Tax |
| Line Total |

### Validation

- Quantity > 0
- Price >= 0

## 6. SALES ORDER MANAGEMENT

### Purpose

Convert approved quotation into executable order.

### Sales Order Fields

| Field |
|---|
| Order Number |
| Customer |
| Quotation Reference |
| Order Date |
| Delivery Date |
| Currency |
| Status |

### Order Number Format

```
SO-2026-000001
```

### Order Status

- Draft
- Confirmed
- Processing
- Partially Delivered
- Delivered
- Closed
- Cancelled

## 7. SALES ORDER BUSINESS RULES

Rule:

Confirmed Order

Reserves Inventory

Rule:

Cancelled Order

Releases Inventory

Rule:

Delivered Order

Eligible For Invoice

## 8. PRICING ENGINE

### Purpose

Centralized pricing management.

### Pricing Types

- Standard Pricing
- Customer Specific Pricing
- Volume Pricing
- Promotional Pricing
- Contract Pricing

### Pricing Hierarchy

```
Contract Price
↓
Customer Price
↓
Volume Price
↓
Standard Price
```

Highest priority wins.

## 9. CONTRACT MANAGEMENT

### Purpose

Manage customer contracts.

### Fields

| Field |
|---|
| Contract Number |
| Customer |
| Start Date |
| End Date |
| Contract Value |
| Status |

### Contract Status

- Draft
- Active
- Expired
- Terminated

## 10. DELIVERY MANAGEMENT

### Purpose

Track order fulfillment.

### Delivery Status

- Pending
- In Progress
- Partially Delivered
- Delivered

### Integration

Depends On:

- Inventory Module
- Warehouse Module

## 11. INVOICE MANAGEMENT

### Purpose

Generate financial documents.

### Invoice Fields

| Field |
|---|
| Invoice Number |
| Customer |
| Invoice Date |
| Due Date |
| Currency |
| Tax Amount |
| Total Amount |

### Invoice Number Format

```
INV-2026-000001
```

### Invoice Status

- Draft
- Posted
- Partially Paid
- Paid
- Cancelled

### Accounting Impact

Invoice Creation:

- Accounts Receivable Dr
- Sales Revenue Cr

Automatic Finance Posting.

## 12. PAYMENT TRACKING

### Purpose

Track customer payments.

### Payment Methods

- Cash
- Bank Transfer
- Cheque
- UPI
- Online Gateway

### Payment Status

- Pending
- Partial
- Paid
- Overdue

## 13. RETURNS MANAGEMENT

### Purpose

Handle customer returns.

### Return Types

- Damaged Goods
- Wrong Item
- Excess Quantity
- Quality Issue

### Return Status

- Requested
- Approved
- Received
- Closed

## 14. CREDIT NOTES

### Purpose

Adjust customer balances.

### Scenarios

- Returns
- Pricing Corrections
- Discount Adjustments

### Accounting Impact

- Sales Return Dr
- Accounts Receivable Cr

## 15. SCREEN INVENTORY

- Quotation Dashboard
- Quotation List
- Quotation Create
- Quotation Details
- Sales Order Dashboard
- Sales Order List
- Sales Order Details
- Invoice Dashboard
- Invoice List
- Payment Dashboard
- Returns Dashboard
- Contract Dashboard

## 16. APPROVAL WORKFLOWS

### Quotation Approval

```
Draft
↓
Sales Manager
↓
Approved
```

### Discount Approval

```
Sales Executive
↓
Sales Manager
↓
Finance Approval
↓
Approved
```

### Credit Note Approval

```
Sales Manager
↓
Finance Manager
↓
Approved
```

## 17. NOTIFICATIONS

Events

- Quotation Approved
- Sales Order Created
- Delivery Completed
- Invoice Generated
- Payment Received
- Payment Overdue

Channels

- Email
- In-App
- WhatsApp

## 18. AUDIT REQUIREMENTS

Track:

- Quotation Changes
- Order Changes
- Invoice Changes
- Payment Updates
- Returns
- Credit Notes

## 19. DATABASE TABLES

- quotations
- quotation_items
- sales_orders
- sales_order_items
- contracts
- deliveries
- invoices
- invoice_items
- payments
- returns
- credit_notes
- pricing_rules

## 20. KEY RELATIONSHIPS

```
Customer
1:N Quotations

Quotation
1:N Quotation Items

Quotation
1:1 Sales Order

Sales Order
1:N Deliveries

Sales Order
1:N Invoices

Invoice
1:N Payments
```

## 21. API SPECIFICATIONS

### Quotation APIs

```
GET /api/v1/quotations

POST /api/v1/quotations

PUT /api/v1/quotations/{id}
```

### Sales Order APIs

```
GET /api/v1/sales-orders

POST /api/v1/sales-orders

PUT /api/v1/sales-orders/{id}
```

### Invoice APIs

```
GET /api/v1/invoices

POST /api/v1/invoices

PUT /api/v1/invoices/{id}
```

### Payment APIs

```
GET /api/v1/payments

POST /api/v1/payments
```

## 22. REPORTS

### Sales Reports

- Sales Revenue Report
- Quotation Conversion Report
- Sales Order Report
- Customer Sales Report
- Product Sales Report
- Invoice Aging Report
- Payment Collection Report
- Returns Analysis Report

## 23. ACCEPTANCE CRITERIA

✅ Quotation creation works

✅ Quotation approval works

✅ Sales Order generation works

✅ Inventory reservation works

✅ Invoice generation works

✅ Finance posting works

✅ Payment tracking works

✅ Returns and Credit Notes work

## 24. UAT SCENARIOS

### UAT-001

Create Quotation

Expected:

Quotation Created Successfully

### UAT-002

Convert Quotation To Sales Order

Expected:

Sales Order Generated

### UAT-003

Create Invoice

Expected:

Invoice Posted To Finance

### UAT-004

Receive Payment

Expected:

Invoice Balance Updated

### UAT-005

Create Return

Expected:

Return Process Initiated

## ARCHITECT REVIEW

FRD-06 Sales Domain is now locked.

### Dependency Chain

```
Foundation
↓
Organization
↓
Master Data
↓
CRM
↓
Sales
↓
Finance
```
