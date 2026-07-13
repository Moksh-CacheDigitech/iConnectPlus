# FRD-15 SUPPLY CHAIN MANAGEMENT (SCM) DOMAIN

## Version
1.0

## Status
Architecture Approved

## Cross References
- Related upstream/downstream: [FRD-07 Procurement Domain](./FRD-07-Procurement-Domain.md), [FRD-08 Inventory & Warehouse Domain](./FRD-08-Inventory-Warehouse-Domain.md), [FRD-13 Manufacturing Domain](./FRD-13-Manufacturing-Domain.md)

## 1. PURPOSE

Supply Chain Management Domain end-to-end material aur product flow ko optimize karega.

### Business Objectives

- Demand Forecasting
- Supply Planning
- Distribution Optimization
- Logistics Visibility
- Supplier Collaboration
- Cost Reduction
- Service Level Improvement

## 2. MODULES COVERED

- Demand Planning
- Demand Forecasting
- Supply Planning
- Distribution Planning
- Logistics Management
- Shipment Tracking
- Supplier Collaboration
- Transportation Management
- Network Planning
- Supply Chain Analytics

## 3. SCM LIFECYCLE

```
Demand Forecast
↓
Supply Plan
↓
Procurement
↓
Manufacturing
↓
Inventory
↓
Distribution
↓
Shipment
↓
Customer
```

## 4. DEMAND PLANNING

### Purpose

Estimate future demand.

### Forecast Inputs

- Sales History
- Sales Orders
- Market Trends
- Seasonality
- Promotions
- Manual Forecast

### Forecast Types

- Monthly
- Quarterly
- Yearly

### Outputs

- Forecast Quantity
- Forecast Revenue
- Forecast Accuracy

## 5. DEMAND FORECASTING

### Methods

- Manual
- Statistical
- AI Based
- Hybrid

### KPIs

- Forecast Accuracy %
- Forecast Bias
- Forecast Error

## 6. SUPPLY PLANNING

### Purpose

Match supply with demand.

### Inputs

- Demand Forecast
- Current Inventory
- Production Capacity
- Open Purchase Orders

### Outputs

- Procurement Plan
- Production Plan
- Transfer Plan

## 7. DISTRIBUTION PLANNING

### Purpose

Allocate inventory across warehouses.

### Planning Factors

- Warehouse Capacity
- Regional Demand
- Transit Time
- Inventory Levels

### Outputs

- Distribution Orders
- Transfer Orders

## 8. LOGISTICS MANAGEMENT

### Purpose

Manage movement of goods.

### Logistics Types

- Inbound Logistics
- Outbound Logistics
- Inter Warehouse Logistics

### Fields

| Field |
|---|
| Shipment Number |
| Carrier |
| Route |
| Dispatch Date |
| Delivery Date |

## 9. SHIPMENT TRACKING

### Purpose

Track deliveries.

### Shipment Status

- Planned
- Dispatched
- In Transit
- Delivered
- Delayed
- Returned

### Tracking Data

- Location
- Carrier
- ETA
- Proof Of Delivery

## 10. SUPPLIER COLLABORATION

### Purpose

Improve supplier coordination.

### Features

- Supplier Portal
- RFQ Responses
- PO Acknowledgement
- Delivery Commitments
- Performance Sharing

### Supplier Actions

- Accept PO
- Reject PO
- Update Delivery Date
- Upload Documents

## 11. TRANSPORTATION MANAGEMENT

### Purpose

Optimize transportation.

### Transport Modes

- Road
- Rail
- Air
- Sea

### Planning Factors

- Cost
- Delivery Time
- Capacity
- Priority

## 12. ROUTE MANAGEMENT

### Purpose

Optimize delivery routes.

### Features

- Route Planning
- Route Optimization
- Route Monitoring

### Outputs

- Distance
- Estimated Cost
- Delivery Time

## 13. NETWORK PLANNING

### Purpose

Optimize supply chain structure.

### Components

- Factories
- Warehouses
- Distribution Centers
- Retail Stores

### Analysis

- Network Cost
- Coverage
- Capacity Utilization

## 14. SUPPLY CHAIN ANALYTICS

### KPIs

- Inventory Turnover
- Fill Rate
- Order Fulfillment Rate
- On Time Delivery
- Lead Time
- Forecast Accuracy
- Logistics Cost

## 15. SCREEN INVENTORY

- SCM Dashboard
- Demand Planning Dashboard
- Forecast Dashboard
- Supply Planning Dashboard
- Distribution Dashboard
- Shipment Dashboard
- Transportation Dashboard
- Supplier Collaboration Portal
- Network Planning Dashboard
- SCM Analytics Dashboard

## 16. APPROVAL WORKFLOWS

### Forecast Approval

```
Planner
↓
Supply Chain Manager
↓
Approved
```

### Supply Plan Approval

```
Planner
↓
Operations Head
↓
Approved
```

### Distribution Plan Approval

```
Distribution Manager
↓
SCM Head
↓
Approved
```

## 17. NOTIFICATIONS

Events

- Forecast Generated
- Supply Shortage
- Shipment Delayed
- PO Acknowledged
- Delivery Completed
- Transportation Exception

Channels

- Email
- In-App
- WhatsApp

## 18. AUDIT REQUIREMENTS

Track:

- Forecast Changes
- Supply Plan Changes
- Shipment Updates
- Route Changes
- Supplier Responses

## 19. DATABASE TABLES

- demand_forecasts
- forecast_versions
- supply_plans
- distribution_plans
- shipments
- shipment_tracking
- carriers
- transport_orders
- routes
- supplier_portal_users
- supplier_acknowledgements
- network_models

## 20. KEY RELATIONSHIPS

```
Forecast
1:N Supply Plans

Supply Plan
1:N Procurement Plans

Supply Plan
1:N Production Plans

Shipment
1:N Tracking Events

Carrier
1:N Shipments

Supplier
1:N Acknowledgements
```

## 21. API SPECIFICATIONS

### Forecast APIs

```
GET /api/v1/forecasts

POST /api/v1/forecasts

PUT /api/v1/forecasts/{id}
```

### Shipment APIs

```
GET /api/v1/shipments

POST /api/v1/shipments

PUT /api/v1/shipments/{id}
```

### Supplier Portal APIs

```
GET /api/v1/suppliers/portal

POST /api/v1/suppliers/acknowledge
```

## 22. REPORTS

### SCM Reports

- Demand Forecast Report
- Forecast Accuracy Report
- Supply Plan Report
- Distribution Report
- Shipment Performance Report
- Transportation Cost Report
- Supplier Collaboration Report
- Network Utilization Report

## 23. ACCEPTANCE CRITERIA

✅ Forecast generated correctly

✅ Supply planning works

✅ Distribution planning works

✅ Shipment tracking works

✅ Supplier collaboration works

✅ Transportation planning works

✅ SCM KPIs calculated

## 24. UAT SCENARIOS

### UAT-001

Generate Forecast

Expected:

Forecast Created Successfully

### UAT-002

Create Supply Plan

Expected:

Supply Plan Generated

### UAT-003

Track Shipment

Expected:

Shipment Status Updated

### UAT-004

Supplier Acknowledges PO

Expected:

Acknowledgement Recorded

### UAT-005

View SCM Dashboard

Expected:

KPIs Displayed Correctly

## ARCHITECT REVIEW

FRD-15 SCM Domain is now locked.

### Critical Observation

SCM module now supports:

- Demand Forecasting
- Supply Planning
- Distribution Planning
- Shipment Visibility
- Transportation Optimization
- Supplier Collaboration
- Supply Chain Analytics
