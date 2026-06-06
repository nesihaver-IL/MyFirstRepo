# Order Management System — Operational Documentation
**Product ID**: order-management
**Version**: 1.0
**Doc Type**: Operational

---

## Overview

The Order Management System (OMS) is the central hub for all order lifecycle operations — from the moment a customer confirms a purchase through delivery confirmation and returns. It acts as the system of record for every order and coordinates communication between the storefront, inventory, fulfillment, and payment systems.

## Core Functions

### Order Creation

When a customer places an order, the OMS:

1. **Receives the order payload** from the Storefront API (product IDs, quantities, customer ID, shipping address, selected payment method).
2. **Validates inventory** — calls the Inventory Service to confirm each item is in stock and reserve the quantity.
3. **Calls the Payment Gateway** — submits a payment authorization (not capture) to hold the funds.
4. **Creates the order record** — persists the order to the Orders Database with status `PENDING_FULFILLMENT`.
5. **Emits `order.created` event** to the Event Bus, triggering the Fulfillment Service and Notification Service in parallel.

### Order Fulfillment Flow

After order creation, the fulfillment lifecycle is:

```
order.created event
        ↓
Fulfillment Service
   → picks items from warehouse
   → prints shipping label (Shipping Provider API)
   → updates order status → SHIPPED
        ↓
OMS receives order.shipped event
   → captures payment (calls Payment Gateway to convert auth → capture)
   → sends shipment confirmation to customer (via Notification Service)
        ↓
Shipping Provider webhook → order.delivered
   → OMS updates status → DELIVERED
   → releases any remaining payment hold
```

### Order Cancellation

An order can be cancelled if it is still in `PENDING_FULFILLMENT` status (before warehouse picks it):

1. OMS calls Inventory Service to release the reserved quantities.
2. OMS calls Payment Gateway to void the authorization (no charge to the customer).
3. OMS updates status → `CANCELLED`.
4. Emits `order.cancelled` event to Notification Service.

If the order is already `SHIPPED`, cancellation is blocked. The customer must initiate a return instead.

### Returns Processing

Returns are handled as a separate order-type (`type: RETURN`) linked to the original order:

1. Customer requests return via Storefront → OMS creates a Return Order.
2. OMS issues a shipping label for the customer to send the item back.
3. On receipt at the warehouse (warehouse scans barcode), OMS triggers:
   - Inventory Service: restocks the item
   - Payment Gateway: initiates refund
   - Notification Service: sends refund confirmation

## Subsystem Relationships

```
Storefront API
        ↓  POST /orders
Order Management System (OMS)
        ↓                    ↓
Inventory Service        Payment Gateway
(reserve stock)          (authorize payment)
        ↓
   Orders Database (POSTGRES — system of record)
        ↓
   Event Bus  ──────────────────────────────────────────┐
        ↓                                               ↓
Fulfillment Service                          Notification Service
(pick → label → ship)                        (email + SMS to customer)
        ↓
Shipping Provider API
(FedEx / UPS / DHL)
        ↓
   Delivery Webhook → back to OMS (status: DELIVERED)
```

## Status Lifecycle

```
PENDING_FULFILLMENT
        ↓  (warehouse picks items)
FULFILLMENT_IN_PROGRESS
        ↓  (label printed, carrier collected)
SHIPPED
        ↓  (carrier delivers)
DELIVERED
```

Cancellation: PENDING_FULFILLMENT → CANCELLED (only from this state)
Returns:       DELIVERED → RETURN_REQUESTED → RETURN_RECEIVED → REFUNDED

## Key Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `payment_capture_mode` | `on_ship` | When to capture payment: `on_order` or `on_ship` |
| `cancellation_window_hours` | 2 | Max hours after order creation to cancel |
| `return_window_days` | 30 | Max days after delivery to request a return |
| `max_items_per_order` | 50 | Per order limit for operational manageability |

## Business Context

The OMS was built to eliminate the "split-brain" problem that existed when order state was managed independently by the Storefront, the Fulfillment team's spreadsheets, and the Finance team's accounting system. These three systems would regularly disagree on order status, leading to:

- Customers receiving duplicate shipments (charged twice)
- Refunds processed for orders that were never returned
- Customer support unable to give a definitive order status

By establishing the OMS as the **single system of record** for all order state, the organization:
- **Reduced order disputes by 78%** in the first quarter after launch
- **Eliminated manual reconciliation** between Fulfillment and Finance (saved 40 person-hours/week)
- **Enabled same-day customer support** — any agent can see exact order state in one lookup
- **Created a reliable audit trail** for revenue recognition and financial compliance

## Related Components

- **Payment Gateway** — OMS calls it for authorization on order creation and capture on shipment
- **Inventory Service** — OMS calls it to reserve and release stock
- **Fulfillment Service** — listens to `order.created` events; reports `order.shipped` back
- **Notification Service** — sends customer emails/SMS at each status transition
- **Event Bus** — the backbone connecting OMS to all downstream consumers
- **Storefront API** — the upstream caller that creates orders and queries status
