# Runbooks

Operational runbooks for the Knowledge Hub Agent.

## Available Runbooks

### [Deployment Runbook](./deployment.md)
Complete procedures for deploying to Dev, Staging, and Production environments.

**Use when**:
- Deploying new version
- Setting up new environment
- Rolling back deployment

**Key sections**:
- Pre-deployment checklist
- Infrastructure deployment steps
- Application deployment
- Post-deployment validation
- Rollback procedures

### [Incident Response Runbook](./incident-response.md)
Procedures for responding to and resolving incidents.

**Use when**:
- Service outage detected
- Performance degradation
- Security incident
- Data loss

**Key sections**:
- Incident classification (P1-P4)
- Response procedures
- Common incident scenarios
- Escalation paths
- Post-incident documentation

### [Scaling Runbook](./scaling.md)
Guide for scaling resources to handle increased load.

**Use when**:
- Performance degradation due to load
- Preparing for expected traffic spike
- Optimizing costs

**Key sections**:
- When to scale (indicators)
- Vertical vs horizontal scaling
- Azure service tier recommendations
- Cost impact analysis
- Post-scaling monitoring

## Quick Reference

### Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| On-Call Engineer | [Phone/Email] | 24/7 |
| Engineering Lead | [Phone/Email] | Business hours |
| Azure Support | +1-800-642-7676 | 24/7 |

### Quick Commands

```bash
# Check service health
curl https://your-webapp.azurewebsites.net/health

# Restart application
az webapp restart --name your-webapp --resource-group rg

# View logs
az webapp log tail --name your-webapp --resource-group rg

# Scale up
az appservice plan update --name your-plan --resource-group rg --sku P1V2
```

### Common Troubleshooting

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| 503 Service Unavailable | App not started | Restart: `az webapp restart` |
| Slow responses | High load | Scale up tier |
| 429 Errors | OpenAI throttling | Increase quota |
| Authentication errors | Token expired | Re-login: `az login` |

## Related Documentation

- [Operations Quick Start Guide](../operations/quick-start-guide.md)
- [Troubleshooting Guide](../troubleshooting.md)
- [Monitoring Guide](../operations/monitoring-guide.md)
- [Production Checklist](../operations/production-checklist.md)

---

*Last Updated: 2025-01-12*
