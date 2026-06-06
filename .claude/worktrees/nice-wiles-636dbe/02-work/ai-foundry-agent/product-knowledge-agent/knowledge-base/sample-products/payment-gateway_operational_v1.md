# Payment Gateway — Operational Documentation
**Product ID**: payment-gateway
**Version**: 1.0
**Doc Type**: Operational

---

## Overview

The Payment Gateway is the central processing hub for all financial transactions in the platform. It accepts payment requests from customer-facing applications, validates them, routes them to the appropriate payment processor, and returns a standardized response.

## Core Functions

### Transaction Processing

The payment gateway processes transactions in four stages:

1. **Validation** — Checks that the payment request is structurally valid: required fields present, amount > 0, currency code is ISO 4217 compliant, card number passes Luhn check.

2. **Authentication** — Verifies the merchant's API key and confirms the request originates from an authorized IP range. Tokens are validated against the Auth Service (see Subsystem Relationships below).

3. **Routing** — Selects the appropriate payment processor based on card type (Visa → Processor A, Mastercard → Processor B, AMEX → Processor C), transaction amount thresholds, and processor availability.

4. **Settlement** — After processor confirmation, writes the transaction record to the Transactions Database, emits a `transaction.completed` event to the Event Bus, and returns a response to the caller.

### Retry Logic

If a processor returns a transient error (HTTP 503 or timeout), the gateway retries up to 3 times with exponential backoff (1s, 2s, 4s). Permanent failures (HTTP 4xx from processor) are not retried.

### Idempotency

All requests include an `idempotency_key`. If the same key is seen twice within 24 hours, the gateway returns the original response without re-processing.

## Subsystem Relationships

```
Customer App → API Gateway → Payment Gateway
                                 ↓
                           Auth Service (token validation)
                                 ↓
                           Processor Router
                                 ↓
                    ┌────────────┼────────────┐
                Processor A  Processor B  Processor C
                                 ↓
                        Transactions Database
                                 ↓
                          Event Bus (transaction.completed)
                                 ↓
               ┌─────────────────┼──────────────────┐
          Notification       Reporting           Fraud Detection
          Service            Module              Service
```

## Key Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_retries` | 3 | Max retry attempts on transient processor errors |
| `timeout_ms` | 5000 | Per-processor request timeout |
| `idempotency_ttl_hours` | 24 | How long idempotency keys are remembered |
| `rate_limit_rps` | 500 | Max requests per second per merchant |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| PGW-001 | Validation failed | Fix request and retry |
| PGW-002 | Authentication failed | Check API key |
| PGW-003 | Processor unavailable | Automatic retry; escalate if persistent |
| PGW-004 | Duplicate idempotency key | Check original transaction |
| PGW-005 | Rate limit exceeded | Implement client-side rate limiting |

## Business Context

The Payment Gateway exists to decouple merchant applications from the complexity of managing multiple payment processor integrations. Without it, every merchant application would need to implement Visa, Mastercard, and AMEX protocols independently, leading to duplicated code, inconsistent error handling, and difficult PCI-DSS compliance auditing.

By centralizing all payment processing, the organization achieves:
- **Single PCI-DSS audit scope** — only the gateway is in scope, not every application
- **Processor redundancy** — automatic failover between processors ensures high availability
- **Unified transaction reporting** — all transactions flow through one system
