# Production Deployment Checklist

Complete checklist for deploying Knowledge Hub Agent to production.

## Pre-Production Readiness

### Security [ ]

- [ ] **CORS configured** with specific origins (not "*")
- [ ] **HTTPS enforced** on all endpoints
- [ ] **API authentication** implemented (Azure AD / API keys)
- [ ] **Network security groups** configured
- [ ] **Azure Private Link** enabled for sensitive resources
- [ ] **Key Vault** access policies restricted
- [ ] **Managed Identity** enabled and configured
- [ ] **Secrets removed** from code (use Key Vault)
- [ ] **DDoS protection** enabled
- [ ] **WAF (Web Application Firewall)** configured
- [ ] **Security headers** set (HSTS, CSP, X-Frame-Options)
- [ ] **Input validation** on all API endpoints
- [ ] **Rate limiting** implemented
- [ ] **Audit logging** enabled

### Performance [ ]

- [ ] **App Service tier** appropriate for load (S1+ for production)
- [ ] **Auto-scaling rules** configured
- [ ] **Azure OpenAI quota** sufficient (default 240K TPM may be too low)
- [ ] **CDN configured** for static assets (if applicable)
- [ ] **Database indexes** optimized (if using database)
- [ ] **Caching strategy** implemented (Redis recommended)
- [ ] **Connection pooling** configured
- [ ] **Async operations** used where appropriate
- [ ] **Load testing completed** (500+ concurrent users)
- [ ] **Performance benchmarks** documented

### Monitoring & Observability [ ]

- [ ] **Application Insights** configured with alerts
- [ ] **Alert rules** created for critical metrics:
  - Response time > 5s
  - Error rate > 1%
  - CPU > 80%
  - Memory > 85%
  - HTTP 5xx errors
- [ ] **Log Analytics workspace** set up
- [ ] **Custom metrics** tracked (agent queries, document retrievals)
- [ ] **Dashboards created** for operations team
- [ ] **Availability tests** configured (ping tests from multiple regions)
- [ ] **Status page** set up (e.g., status.yourcompany.com)
- [ ] **On-call rotation** established
- [ ] **Incident response plan** documented

### Reliability [ ]

- [ ] **Backup strategy** defined and tested
- [ ] **Disaster recovery plan** documented
- [ ] **RTO/RPO defined** (Recovery Time/Point Objectives)
- [ ] **Multi-region deployment** (if HA required)
- [ ] **Health check endpoint** implemented and tested
- [ ] **Graceful degradation** for dependencies
- [ ] **Circuit breakers** implemented for external services
- [ ] **Retry logic** with exponential backoff
- [ ] **Timeout configuration** appropriate
- [ ] **Database backups** automated (if applicable)

### Compliance & Legal [ ]

- [ ] **Data privacy** requirements met (GDPR, CCPA, etc.)
- [ ] **Data retention** policies defined
- [ ] **Terms of Service** reviewed
- [ ] **SLA commitments** defined
- [ ] **Compliance certifications** verified (SOC 2, ISO 27001)
- [ ] **Data residency** requirements met
- [ ] **Audit trail** for compliance
- [ ] **PIPEDA compliance** (if Canadian data)

### Documentation [ ]

- [ ] **Architecture diagram** up to date
- [ ] **Runbooks** complete (deployment, incident response, scaling)
- [ ] **API documentation** published
- [ ] **User documentation** available
- [ ] **Operations manual** written
- [ ] **Troubleshooting guide** complete
- [ ] **Contact information** documented
- [ ] **Escalation paths** defined

### Cost Optimization [ ]

- [ ] **Cost alerts** configured
- [ ] **Resource tagging** for cost allocation
- [ ] **Unused resources** identified and removed
- [ ] **Reserved instances** considered (1-3 year commitment)
- [ ] **Auto-shutdown** for non-production environments
- [ ] **Cost optimization recommendations** reviewed

## Deployment Day Checklist

### Pre-Deployment (T-24 hours) [ ]

- [ ] **Stakeholders notified** of deployment window
- [ ] **Change request approved**
- [ ] **Maintenance window scheduled**
- [ ] **Rollback plan prepared** and tested
- [ ] **Backup taken** of current production
- [ ] **Team availability** confirmed (on-call)
- [ ] **Support team briefed**

### Deployment (T-0) [ ]

- [ ] **Pre-deployment checks** completed
- [ ] **Infrastructure deployed** (via Bicep)
- [ ] **Application deployed**
- [ ] **Configuration updated**
- [ ] **Database migrations** run (if applicable)
- [ ] **Smoke tests** passed
- [ ] **Health checks** green

### Post-Deployment (T+1 hour) [ ]

- [ ] **Functional tests** passed
- [ ] **Performance metrics** normal
- [ ] **Error rates** acceptable (<1%)
- [ ] **User acceptance testing** completed
- [ ] **Monitoring dashboards** reviewed
- [ ] **Status page** updated
- [ ] **Stakeholders notified** of completion

### Post-Deployment (T+24 hours) [ ]

- [ ] **No critical issues** reported
- [ ] **Performance stable**
- [ ] **User feedback** positive
- [ ] **Deployment documented**
- [ ] **Lessons learned** captured

## Production Configuration

### Recommended Settings

```ini
# .env.production
AZURE_SUBSCRIPTION_ID=<your-subscription-id>
AZURE_RESOURCE_GROUP=knowledge-hub-prod-rg
AZURE_PROJECT_NAME=knowledge-hub-prod-project

AGENT_MODEL=gpt-4o
AGENT_TEMPERATURE=0.3
USE_FILE_SEARCH=true

# Production API settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Enable all monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=<connection-string>
ENABLE_TELEMETRY=true
```

### Azure Resource Tiers

**Recommended for Production**:
- **App Service**: S1 or P1V2 minimum
- **Azure OpenAI**: Standard tier with increased quota
- **Azure AI Search**: Standard tier (not Basic)
- **Application Insights**: Pay-as-you-go

## Security Hardening

### CORS Configuration

```python
# src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],  # NOT "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only what you need
    allow_headers=["Content-Type", "Authorization"],
)
```

### API Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify Azure AD token."""
    token = credentials.credentials
    # Implement Azure AD token validation
    # https://learn.microsoft.com/azure/active-directory/develop/access-tokens
    return token

@app.post("/query")
async def query(request: QueryRequest, token: str = Depends(verify_token)):
    # Protected endpoint
    pass
```

## Go-Live Approval

**Approval Required From**:
- [ ] Engineering Lead
- [ ] Security Team
- [ ] Operations Team
- [ ] Product Owner
- [ ] Legal/Compliance (if applicable)

**Sign-off**:
```
Approved by: _________________  Date: _________
Role: _________________
```

---

*Last Updated: 2025-01-12*
