# Incident Response Runbook

## Incident Classification

### Severity Levels

**P1 - Critical**
- Service completely down
- Security breach
- Data loss
- Impact: All users, >50% degradation
- Response Time: 15 minutes
- Resolution Target: 4 hours

**P2 - High**
- Major functionality broken
- Performance severely degraded
- Impact: >25% of users
- Response Time: 30 minutes
- Resolution Target: 8 hours

**P3 - Medium**
- Minor functionality issues
- Workaround available
- Impact: <25% of users
- Response Time: 2 hours
- Resolution Target: 24 hours

**P4 - Low**
- Cosmetic issues
- Feature requests
- Impact: Minimal
- Response Time: 24 hours
- Resolution Target: Next release

## Incident Response Flow

```
Incident Detected → Classify → Notify → Investigate → Mitigate → Resolve → Document
```

## Response Procedures

### P1 - Critical Incident

**1. Immediate Actions** (0-15 min)
```bash
# Declare incident
echo "P1 INCIDENT: [Description]" | tee incident.log

# Check service health
curl https://your-webapp.azurewebsites.net/health

# Check Azure service status
az webapp show --name your-webapp --resource-group rg --query state

# Quick diagnostics
az monitor app-insights query \
  --app your-insights \
  --resource-group rg \
  --analytics-query "exceptions | where timestamp > ago(1h) | take 50"
```

**2. Notify Stakeholders**
- Incident Commander
- On-call engineers
- Management (for P1)
- Customer support team

**3. Establish Communication Channel**
- Create incident Slack channel or Teams chat
- Set up status page update process

**4. Investigation**
```bash
# View recent logs
az webapp log tail --name your-webapp --resource-group rg

# Check error rates
az monitor metrics list \
  --resource <webapp-resource-id> \
  --metric "Http5xx" \
  --start-time $(date -u -d '1 hour ago' '+%Y-%m-%dT%H:%M:%S')

# Review recent deployments
az webapp deployment list --name your-webapp --resource-group rg
```

**5. Mitigation Options**
- **Option A**: Rollback to previous version
  ```bash
  # See deployment.md for rollback procedures
  ```

- **Option B**: Scale up resources
  ```bash
  az appservice plan update --name your-plan --resource-group rg --sku P1V2
  ```

- **Option C**: Restart services
  ```bash
  az webapp restart --name your-webapp --resource-group rg
  ```

**6. Resolution Verification**
- Run health checks
- Monitor error rates for 30 minutes
- Confirm with affected users

**7. Post-Incident**
- Update status page
- Schedule post-mortem within 48 hours
- Document lessons learned

### Common Incidents

#### Service Unavailable (503)

**Symptoms**: API returns 503, health check fails

**Quick Checks**:
```bash
# 1. Check if app is running
az webapp show --name your-webapp --resource-group rg --query state

# 2. Check recent errors
az monitor app-insights query \
  --app your-insights \
  --resource-group rg \
  --analytics-query "traces | where severityLevel >= 3 | order by timestamp desc | take 20"

# 3. Check authentication
az account show
```

**Resolution**:
1. Restart app if hung: `az webapp restart --name your-webapp --resource-group rg`
2. Check environment variables configured correctly
3. Verify Azure credentials are valid
4. Check Azure OpenAI quota not exceeded

#### Slow Response Times

**Symptoms**: Response time >10 seconds

**Quick Checks**:
```bash
# Check Azure OpenAI throttling
az monitor app-insights query \
  --app your-insights \
  --resource-group rg \
  --analytics-query "requests | where resultCode == 429 | summarize count() by bin(timestamp, 5m)"

# Check CPU/Memory
az monitor metrics list \
  --resource <webapp-resource-id> \
  --metric "CpuPercentage,MemoryPercentage"
```

**Resolution**:
1. Scale up App Service tier
2. Increase Azure OpenAI quota
3. Implement caching
4. Optimize vector store queries

#### Authentication Failures

**Symptoms**: 401/403 errors

**Resolution**:
```bash
# Re-login to Azure
az login
az account set --subscription "your-sub-id"

# Verify managed identity (if using)
az webapp identity show --name your-webapp --resource-group rg

# Check role assignments
az role assignment list --assignee <principal-id>
```

## Escalation Path

1. **L1 Support** → Initial triage, known issues
2. **L2 Engineering** → Investigation, mitigation
3. **L3 Senior Engineering** → Complex issues, architecture changes
4. **Management** → Business impact decisions
5. **Azure Support** → Platform-level issues

## Incident Documentation Template

```markdown
# Incident Report: [Title]

**Incident ID**: INC-20250112-001
**Severity**: P1
**Start Time**: 2025-01-12 10:30 UTC
**End Time**: 2025-01-12 12:45 UTC
**Duration**: 2h 15m

## Summary
Brief description of what happened

## Impact
- Users affected: 100%
- Services impacted: API queries
- Business impact: Revenue loss, reputation

## Timeline
- 10:30 - Incident detected via monitoring alert
- 10:35 - P1 declared, team notified
- 10:45 - Root cause identified (Azure OpenAI quota)
- 11:00 - Mitigation applied (quota increased)
- 11:15 - Service restored
- 12:45 - All clear, monitoring normal

## Root Cause
Detailed explanation of why it happened

## Resolution
What was done to fix it

## Prevention
- Action items to prevent recurrence
- Monitoring improvements
- Process changes

## Lessons Learned
What we learned from this incident
```

## Tools & Resources

### Monitoring
- Application Insights: https://portal.azure.com → Application Insights
- Azure Monitor: https://portal.azure.com → Monitor

### Logs
```bash
# Stream logs
az webapp log tail --name your-webapp --resource-group rg

# Download logs
az webapp log download --name your-webapp --resource-group rg --log-file logs.zip
```

### Quick Commands
```bash
# Health check
curl https://your-webapp.azurewebsites.net/health

# Restart app
az webapp restart --name your-webapp --resource-group rg

# Scale up
az appservice plan update --name your-plan --resource-group rg --sku P1V2

# View metrics
az monitor metrics list --resource <resource-id> --metric "Http5xx,ResponseTime"
```

---

*Last Updated: 2025-01-12*
