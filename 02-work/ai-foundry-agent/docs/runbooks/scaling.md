# Scaling Runbook

## When to Scale

### Indicators

**Scale Up (Vertical) When**:
- CPU usage consistently >70%
- Memory usage consistently >80%
- Response time >5 seconds average
- Azure OpenAI throttling (429 errors)

**Scale Out (Horizontal) When**:
- Request rate >1000 req/min
- Multiple regions needed
- High availability requirements

## Scaling Options

### App Service Scaling

**Vertical Scaling** (More powerful instance):
```bash
# Check current tier
az appservice plan show \
  --name your-plan \
  --resource-group knowledge-hub-rg \
  --query sku.name

# Scale up to Standard
az appservice plan update \
  --name your-plan \
  --resource-group knowledge-hub-rg \
  --sku S1

# Scale up to Premium
az appservice plan update \
  --name your-plan \
  --resource-group knowledge-hub-rg \
  --sku P1V2
```

**Horizontal Scaling** (More instances):
```bash
# Manual scaling
az appservice plan update \
  --name your-plan \
  --resource-group knowledge-hub-rg \
  --number-of-workers 3

# Auto-scaling rules
az monitor autoscale create \
  --resource-group knowledge-hub-rg \
  --resource your-webapp \
  --resource-type Microsoft.Web/serverfarms \
  --name autoscale-rule \
  --min-count 2 \
  --max-count 10 \
  --count 2

# CPU-based rule
az monitor autoscale rule create \
  --resource-group knowledge-hub-rg \
  --autoscale-name autoscale-rule \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1
```

### Azure OpenAI Scaling

**Increase Token Quota**:
```bash
# Check current usage
az cognitiveservices account list-usage \
  --name your-openai \
  --resource-group knowledge-hub-rg

# Request quota increase via Azure Portal:
# Portal → Azure OpenAI → Quotas → Request Increase
```

**Deploy Additional Models**:
```bash
# Deploy another GPT-4o instance
az cognitiveservices account deployment create \
  --name your-openai \
  --resource-group knowledge-hub-rg \
  --deployment-name gpt-4o-2 \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 50 \
  --sku-name Standard
```

### Azure AI Search Scaling

**Upgrade Tier**:
```bash
# Check current tier
az search service show \
  --name your-search \
  --resource-group knowledge-hub-rg \
  --query sku.name

# Upgrade to Standard2
az search service update \
  --name your-search \
  --resource-group knowledge-hub-rg \
  --partition-count 2 \
  --replica-count 2
```

## Performance Tiers

| Tier | Use Case | Cost/Month | Max Performance |
|------|----------|------------|-----------------|
| **Basic (B1)** | Development | ~$15 | 100 req/min |
| **Standard (S1)** | Small Production | ~$70 | 500 req/min |
| **Premium (P1V2)** | Production | ~$140 | 2000 req/min |
| **Premium (P3V2)** | High Scale | ~$560 | 10000 req/min |

## Cost Impact Analysis

**Before Scaling**:
```bash
# Estimate current costs
az consumption usage list \
  --start-date 2025-01-01 \
  --end-date 2025-01-12 \
  | jq '[.[] | select(.instanceName | contains("knowledge-hub"))] | group_by(.meterCategory) | map({category: .[0].meterCategory, cost: map(.pretaxCost) | add})'
```

**Scaling Impact**:
- B1 → S1: +$55/month
- S1 → P1V2: +$70/month
- Adding 2 instances: 2x current tier cost

## Monitoring After Scaling

```bash
# Monitor for 24 hours
az monitor metrics list \
  --resource <webapp-resource-id> \
  --metric "CpuPercentage,MemoryPercentage,Http5xx,ResponseTime" \
  --start-time $(date -u -d '1 day ago' '+%Y-%m-%dT%H:%M:%S')

# Check if scaling helped
az monitor app-insights query \
  --app your-insights \
  --resource-group knowledge-hub-rg \
  --analytics-query "requests | where timestamp > ago(24h) | summarize avg(duration), percentile(duration, 95) by bin(timestamp, 1h)"
```

## Rollback Scaling

If scaling doesn't help or causes issues:

```bash
# Scale back down
az appservice plan update \
  --name your-plan \
  --resource-group knowledge-hub-rg \
  --sku B1

# Reduce instances
az appservice plan update \
  --name your-plan \
  --resource-group knowledge-hub-rg \
  --number-of-workers 1
```

---

*Last Updated: 2025-01-12*
