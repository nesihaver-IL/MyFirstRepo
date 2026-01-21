# Monitoring Guide

Comprehensive guide for monitoring the Knowledge Hub Agent in production.

## Key Metrics

### Application Performance

| Metric | Target | Alert Threshold | Critical Threshold |
|--------|--------|-----------------|-------------------|
| **Response Time** | <2s avg | >5s | >10s |
| **Error Rate** | <0.1% | >1% | >5% |
| **Availability** | >99.9% | <99.5% | <99% |
| **Throughput** | - | Baseline ±50% | Baseline ±100% |

### Resource Utilization

| Resource | Normal | Warning | Critical |
|----------|--------|---------|----------|
| **CPU** | <50% | >70% | >90% |
| **Memory** | <60% | >80% | >95% |
| **Network** | <50% | >70% | >90% |
| **Disk I/O** | <50% | >70% | >90% |

## Application Insights Setup

### View Metrics

```bash
# Portal: Azure Portal → Application Insights → your-insights → Metrics

# CLI: List available metrics
az monitor app-insights metrics show \
  --app your-insights \
  --resource-group knowledge-hub-rg \
  --metric requests/count

# Common metrics:
# - requests/count (Request rate)
# - requests/duration (Response time)
# - requests/failed (Failed requests)
# - exceptions/count (Exceptions)
# - performanceCounters/processCpuPercentage (CPU)
# - performanceCounters/processPrivateBytes (Memory)
```

### Useful Queries

```kusto
// Recent errors (last hour)
traces
| where severityLevel >= 3
| where timestamp > ago(1h)
| order by timestamp desc
| take 50

// Slow requests (>5 seconds)
requests
| where duration > 5000
| where timestamp > ago(24h)
| project timestamp, name, duration, resultCode, url
| order by duration desc

// Error rate over time
requests
| where timestamp > ago(24h)
| summarize 
    total = count(),
    failed = countif(success == false)
    by bin(timestamp, 5m)
| extend errorRate = (failed * 100.0) / total
| project timestamp, errorRate

// Agent query performance
customEvents
| where name == "agent_query"
| where timestamp > ago(24h)
| summarize 
    avg(duration),
    percentile(duration, 50),
    percentile(duration, 95),
    percentile(duration, 99)
    by bin(timestamp, 1h)

// Top errors
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc
| take 10

// User activity
customEvents
| where name == "query_completed"
| where timestamp > ago(24h)
| summarize queries = count() by bin(timestamp, 1h)
| render timechart
```

## Alert Configuration

### Create Alert Rules

```bash
# CPU Alert
az monitor metrics alert create \
  --name "High CPU Usage" \
  --resource-group knowledge-hub-rg \
  --scopes $(az webapp show --name your-webapp --resource-group knowledge-hub-rg --query id -o tsv) \
  --condition "avg CpuPercentage > 80" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action $(az monitor action-group show --name ops-team --resource-group knowledge-hub-rg --query id -o tsv)

# Error Rate Alert
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group knowledge-hub-rg \
  --scopes $(az monitor app-insights component show --app your-insights --resource-group knowledge-hub-rg --query id -o tsv) \
  --condition "count requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m
```

### Recommended Alerts

1. **Response Time** > 5 seconds (Warning), > 10 seconds (Critical)
2. **Error Rate** > 1% (Warning), > 5% (Critical)
3. **CPU Usage** > 70% (Warning), > 90% (Critical)
4. **Memory Usage** > 80% (Warning), > 95% (Critical)
5. **HTTP 5xx Errors** > 10/5min (Warning), > 50/5min (Critical)
6. **Availability** < 99.5% (Warning), < 99% (Critical)

## Dashboard Setup

### Create Azure Dashboard

1. Go to Azure Portal → Dashboards → New dashboard
2. Add tiles:
   - Request rate (line chart)
   - Response time (line chart)
   - Error rate (metric)
   - CPU/Memory (gauges)
   - Recent errors (grid)

### Grafana Integration (Optional)

```bash
# Install Grafana plugin for Azure Monitor
grafana-cli plugins install grafana-azure-monitor-datasource

# Configure datasource in Grafana UI
# Add panels for key metrics
```

## Availability Monitoring

```bash
# Create availability test
az monitor app-insights web-test create \
  --resource-group knowledge-hub-rg \
  --app your-insights \
  --name "Health Check Test" \
  --location "East US" \
  --kind "ping" \
  --frequency 300 \
  --timeout 120 \
  --locations "Central US" "West Europe" "Southeast Asia" \
  --test-url "https://your-webapp.azurewebsites.net/health"
```

## Log Retention

```bash
# Set retention period (30-730 days)
az monitor app-insights component update \
  --app your-insights \
  --resource-group knowledge-hub-rg \
  --retention-time 90
```

## Performance Baselines

Document normal operating ranges:

```markdown
**Baseline Metrics** (Updated: 2025-01-12)

| Metric | Normal Range | Peak | Off-Peak |
|--------|--------------|------|----------|
| Request Rate | 50-200/min | 300/min | 20/min |
| Response Time | 1-3s | 4s | 1s |
| CPU | 30-50% | 70% | 20% |
| Memory | 40-60% | 75% | 35% |
| Error Rate | 0.01-0.1% | 0.2% | 0.01% |
```

## Monitoring Checklist

### Daily [ ]
- [ ] Check dashboard for anomalies
- [ ] Review any alerts triggered
- [ ] Check error logs for new issues

### Weekly [ ]
- [ ] Review performance trends
- [ ] Analyze slow queries
- [ ] Check resource utilization trends
- [ ] Review user activity patterns

### Monthly [ ]
- [ ] Update performance baselines
- [ ] Review alert thresholds
- [ ] Audit log retention
- [ ] Cost analysis

---

*Last Updated: 2025-01-12*
