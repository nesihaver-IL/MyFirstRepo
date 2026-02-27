# Authentication Service — Business Case & Architecture
**Product ID**: auth-service
**Version**: 1.0
**Doc Type**: Business Case

---

## What the Auth Service Is

The Authentication Service (Auth Service) is a dedicated microservice responsible for:
- Verifying the identity of users and API clients
- Issuing and validating JWT access tokens
- Managing session lifecycle (creation, refresh, revocation)
- Enforcing multi-factor authentication (MFA) policies

It is consumed by every other service in the platform that needs to know "who is making this request."

## Business Problem It Solves

Before the Auth Service existed, authentication logic was duplicated across 8 separate product teams. Each team implemented login, token validation, and session management independently, resulting in:

1. **Inconsistent security posture** — some teams used MD5 password hashing (deprecated), others used bcrypt. Token expiry policies varied from 1 hour to 30 days with no justification.
2. **Audit failures** — during a security audit, auditors found 4 different authentication implementations with different logging formats, making it impossible to produce a unified access log.
3. **High maintenance cost** — when a CVE was discovered in a JWT library, it had to be patched in 8 places simultaneously, requiring coordinated deployments across 4 teams.

The Auth Service solves all three problems by centralizing all authentication logic into a single, audited, tested service.

## Subsystem Relationships

```
External Client (browser, mobile app, API client)
        ↓
    API Gateway (validates that a token is present)
        ↓ (forwards to Auth Service for validation)
    Auth Service
        ↓                           ↓
  User Database              Token Cache (Redis)
  (identity store)           (fast token lookup)
        ↓
  Audit Log Service (writes every auth event)
        ↓
  Downstream Services (Payment Gateway, Order Management, etc.)
    ← Auth Service answers: "is this token valid and who does it belong to?"
```

## Key Capabilities

### Token Issuance

On successful login, the Auth Service issues:
- **Access token** — JWT, 15-minute TTL, signed with RSA-256
- **Refresh token** — opaque random string, 7-day TTL, stored in Redis

### Token Validation

Every API request that reaches a downstream service includes the access token. The service calls the Auth Service's `/validate` endpoint. The Auth Service:
1. Checks token signature (RSA-256 public key)
2. Checks expiry claim
3. Checks against revocation list in Redis

The entire validation path is under 5ms at p99.

### MFA Enforcement

For high-risk operations (wire transfers, password change, admin actions), the Auth Service can be configured to require a second factor (TOTP, SMS OTP, or hardware key).

### Session Management

Sessions can be revoked immediately (e.g., on "log out all devices"). Revoked tokens are added to the Redis revocation list with a TTL equal to the token's remaining lifetime.

## Business Value

| Before Auth Service | After Auth Service |
|--------------------|-------------------|
| 8 auth implementations | 1 central implementation |
| 4 different audit log formats | 1 unified audit log |
| CVE patch requires 8 deployments | CVE patch requires 1 deployment |
| Auth bugs found in production | Auth bugs found in 1 service's test suite |
| PCI-DSS: 8 services in scope | PCI-DSS: 1 service in scope |

## Related Components

- **API Gateway** — checks that tokens are present before forwarding requests; calls Auth Service for full validation on sensitive endpoints
- **Payment Gateway** — validates payment request tokens via Auth Service before processing
- **User Database** — Auth Service is the only service that reads/writes to the identity store
- **Audit Log Service** — receives all authentication events for compliance reporting
- **Redis Cache** — stores refresh tokens and the revocation list
