# AWS Free Tier Setup & Cost Monitoring Guide for Bedrock Agents

## Overview
This guide explains how to check your current AWS setup, monitor costs, and configure your Bedrock Agent to minimize expenses while staying within AWS Free Tier limits where possible.

---

## Table of Contents
1. [Understanding AWS Bedrock Costs](#understanding-aws-bedrock-costs)
2. [Checking Your Current AWS Setup](#checking-your-current-aws-setup)
3. [Free Tier Components & Alternatives](#free-tier-components--alternatives)
4. [Cost Monitoring & Control](#cost-monitoring--control)
5. [Minimal Cost Architecture](#minimal-cost-architecture)
6. [Budget-Friendly Best Practices](#budget-friendly-best-practices)

---

## Understanding AWS Bedrock Costs

### Important: Bedrock is NOT Free Tier Eligible
**AWS Bedrock does NOT have a free tier.** You will be charged for:
- **Model inference**: Per 1,000 input/output tokens
- **Agent invocations**: Per request + token usage
- **Knowledge bases**: Storage + vector database + embeddings

### Estimated Minimal Costs (Testing Phase)
```
Component                    Estimated Cost/Month
─────────────────────────────────────────────────
Claude 3 Haiku (cheapest)    $5-15 (light testing)
Claude 3 Sonnet              $15-30 (light testing)
Knowledge Base (optional)     $5-20 (OpenSearch Serverless)
Lambda functions             FREE (1M requests/month)
S3 storage                   FREE (5GB for 12 months)
CloudWatch Logs              FREE (5GB ingestion)
─────────────────────────────────────────────────
MINIMUM MONTHLY COST:        $5-50 (depending on usage)
```

**Reality Check:** You cannot run Bedrock Agents at zero cost. However, you can minimize costs significantly.

---

## Checking Your Current AWS Setup

### Step 1: Check What's Currently Deployed

#### 1.1 List All Bedrock Agents
```bash
# Using AWS CLI
aws bedrock-agent list-agents --region us-east-1

# Save output for review
aws bedrock-agent list-agents --region us-east-1 > my-agents.json
```

**Expected Output:**
```json
{
  "agentSummaries": [
    {
      "agentId": "AGENT123",
      "agentName": "MyAgent",
      "agentStatus": "PREPARED",
      "updatedAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### 1.2 Check Bedrock Model Access
```bash
# List all models you have access to
aws bedrock list-foundation-models --region us-east-1 | jq '.modelSummaries[] | {modelId, modelName}'

# Check specific model pricing tier
aws bedrock list-foundation-models --region us-east-1 | jq '.modelSummaries[] | select(.modelId | contains("claude"))'
```

#### 1.3 List Knowledge Bases
```bash
# List all knowledge bases
aws bedrock-agent list-knowledge-bases --region us-east-1

# Get details of specific knowledge base
aws bedrock-agent get-knowledge-base --knowledge-base-id KB_ID --region us-east-1
```

#### 1.4 List Lambda Functions (Action Groups)
```bash
# List Lambda functions (filter for agent-related)
aws lambda list-functions --region us-east-1 | jq '.Functions[] | select(.FunctionName | contains("bedrock") or contains("agent"))'

# Get specific function details
aws lambda get-function --function-name YOUR_FUNCTION_NAME --region us-east-1
```

#### 1.5 Check S3 Buckets (Knowledge Base Storage)
```bash
# List all S3 buckets
aws s3 ls

# Check bucket size (for cost estimation)
aws s3 ls s3://your-kb-bucket --recursive --summarize --human-readable
```

#### 1.6 List OpenSearch Serverless Collections (Vector DB)
```bash
# List OpenSearch Serverless collections
aws opensearchserverless list-collections --region us-east-1

# Get collection details
aws opensearchserverless get-collection --id COLLECTION_ID --region us-east-1
```

---

### Step 2: Check Current Usage & Costs

#### 2.1 AWS Cost Explorer (Console Method)
1. Go to **AWS Console** → **Billing** → **Cost Explorer**
2. Select **Date Range**: Last 30 days
3. **Group by**: Service
4. Look for these services:
   - Amazon Bedrock
   - AWS Lambda
   - Amazon S3
   - Amazon OpenSearch Service
   - CloudWatch

#### 2.2 AWS Cost Explorer (CLI Method)
```bash
# Get cost for last 30 days
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=SERVICE

# Get Bedrock-specific costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --filter file://bedrock-filter.json
```

**bedrock-filter.json:**
```json
{
  "Dimensions": {
    "Key": "SERVICE",
    "Values": ["Amazon Bedrock"]
  }
}
```

#### 2.3 Check CloudWatch Metrics for Usage
```bash
# Get Bedrock invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name Invocations \
  --dimensions Name=AgentId,Value=YOUR_AGENT_ID \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum \
  --region us-east-1

# Get token usage (if available)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name InputTokens \
  --dimensions Name=AgentId,Value=YOUR_AGENT_ID \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum \
  --region us-east-1
```

#### 2.4 Generate Complete Infrastructure Report
```bash
#!/bin/bash
# save as check-aws-setup.sh

echo "=== AWS Bedrock Agent Setup Report ==="
echo ""

echo "1. BEDROCK AGENTS:"
aws bedrock-agent list-agents --region us-east-1 | jq -r '.agentSummaries[] | "  - \(.agentName) (ID: \(.agentId), Status: \(.agentStatus))"'
echo ""

echo "2. KNOWLEDGE BASES:"
aws bedrock-agent list-knowledge-bases --region us-east-1 | jq -r '.knowledgeBaseSummaries[] | "  - \(.name) (ID: \(.knowledgeBaseId))"'
echo ""

echo "3. LAMBDA FUNCTIONS (Agent-related):"
aws lambda list-functions --region us-east-1 | jq -r '.Functions[] | select(.FunctionName | contains("bedrock") or contains("agent")) | "  - \(.FunctionName) (Runtime: \(.Runtime))"'
echo ""

echo "4. S3 BUCKETS (KB storage):"
aws s3 ls | grep -i bedrock || echo "  - No bedrock-related buckets found"
echo ""

echo "5. OPENSEARCH COLLECTIONS:"
aws opensearchserverless list-collections --region us-east-1 | jq -r '.collectionSummaries[] | "  - \(.name) (ID: \(.id))"'
echo ""

echo "6. RECENT COSTS (Last 7 days):"
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '7 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --group-by Type=SERVICE | jq -r '.ResultsByTime[-1].Groups[] | select(.Metrics.UnblendedCost.Amount | tonumber > 0) | "  - \(.Keys[0]): $\(.Metrics.UnblendedCost.Amount)"'

echo ""
echo "=== END REPORT ==="
```

**Run the report:**
```bash
chmod +x check-aws-setup.sh
./check-aws-setup.sh
```

---

## Free Tier Components & Alternatives

### What's Free (Within Limits)

#### 1. AWS Lambda (Action Groups)
**Free Tier:**
- ✅ **1 million requests per month** (permanent free tier)
- ✅ **400,000 GB-seconds of compute** per month
- ✅ Perfect for Bedrock Agent action groups

**Best Practice:**
```python
# Keep Lambda functions lightweight
# Minimize cold start times
# Use Python 3.12 or Node.js 20 (fastest)

def lambda_handler(event, context):
    # Minimal, focused logic only
    # No heavy dependencies
    return result
```

#### 2. Amazon S3 (Document Storage)
**Free Tier (First 12 months):**
- ✅ **5 GB of standard storage**
- ✅ **20,000 GET requests**
- ✅ **2,000 PUT requests**

**After 12 months:**
- Small storage is very cheap (~$0.023/GB/month)

**Best Practice:**
```bash
# Store only essential documents
# Use efficient formats (plain text > PDF)
# Compress large files
# Clean up old versions

aws s3 sync ./docs s3://my-kb-bucket --delete --size-only
```

#### 3. CloudWatch Logs
**Free Tier:**
- ✅ **5 GB of log data ingestion**
- ✅ **5 GB of log data archive**

**Best Practice:**
```bash
# Set log retention to 7 days (not 30)
aws logs put-retention-policy \
  --log-group-name /aws/bedrock/agents/YOUR_AGENT \
  --retention-in-days 7
```

#### 4. CloudWatch Metrics
**Free Tier:**
- ✅ **10 custom metrics**
- ✅ **10 alarms**
- ✅ **1 million API requests**

---

### What's NOT Free (But Can Be Minimized)

#### 1. Amazon Bedrock Model Inference ❌ NOT FREE

**Pricing (as of 2024):**

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| Claude 3 Haiku | $0.00025 | $0.00125 |
| Claude 3 Sonnet | $0.003 | $0.015 |
| Claude 3.5 Sonnet | $0.003 | $0.015 |
| Claude 3 Opus | $0.015 | $0.075 |

**Example Cost Calculation:**
```
Scenario: 100 test conversations per month
Average: 500 input tokens + 300 output tokens per conversation

Using Claude 3 Haiku:
- Input: 100 * 500 * $0.00025/1000 = $0.0125
- Output: 100 * 300 * $0.00125/1000 = $0.0375
- Total: ~$0.05/month

Using Claude 3 Sonnet:
- Input: 100 * 500 * $0.003/1000 = $0.15
- Output: 100 * 300 * $0.015/1000 = $0.45
- Total: ~$0.60/month
```

**Minimization Strategies:**
1. **Use Claude 3 Haiku** for testing (12x cheaper than Sonnet)
2. **Limit agent instructions** to reduce tokens
3. **Cache responses** when possible
4. **Use short, focused test prompts**
5. **Disable agent when not testing**

#### 2. Amazon OpenSearch Serverless (Knowledge Base) ❌ NOT FREE

**Pricing:**
- **Minimum cost: ~$350/month** (1 OCU for indexing + 1 OCU for search)
- This is the MOST EXPENSIVE component

**FREE ALTERNATIVE: Skip Knowledge Bases Initially**

Instead of using Bedrock Knowledge Bases, consider:

**Option A: Use Claude's Built-in Knowledge**
```
Agent Instructions:
"You are an expert in [your domain]. Use your training knowledge
to answer questions about [topic]. When asked about [specific info],
provide [specific guidance]."
```

**Option B: Pass Context Directly in Prompts**
```python
# Read documents locally and pass as context
def invoke_agent_with_context(question, context_docs):
    context = "\n".join([read_file(doc) for doc in context_docs])

    prompt = f"""Context Information:
{context}

User Question: {question}

Answer based on the context above."""

    return invoke_agent(prompt)
```

**Option C: Use S3 + Lambda for Simple RAG**
```python
# Lightweight alternative to OpenSearch
import json
from sentence_transformers import SentenceTransformer

# Store embeddings in S3 as JSON (no vector DB needed)
# Use Lambda to search on-demand
# Only pay for Lambda invocations (FREE tier covers most usage)

def simple_rag_search(query, bucket, embeddings_file):
    # Download embeddings from S3
    # Compute similarity locally
    # Return top results
    # Cost: $0 if within Lambda free tier
```

**Option D: Wait for Production**
- Use knowledge bases only when going to production
- Test thoroughly without knowledge bases first
- Evaluate if the $350/month cost is justified

#### 3. Alternative: Amazon Kendra (Also Expensive) ❌

**Amazon Kendra Pricing:**
- Developer Edition: ~$810/month
- Enterprise Edition: ~$1,008/month
- **Not recommended for budget-conscious projects**

---

## Cost Monitoring & Control

### Step 1: Set Up Billing Alerts

#### 1.1 Create Budget Alert
```bash
# Create a budget via CLI
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget-config.json \
  --notifications-with-subscribers file://budget-notifications.json
```

**budget-config.json:**
```json
{
  "BudgetName": "BedrockMonthlyBudget",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "Service": ["Amazon Bedrock", "Amazon OpenSearch Service"]
  }
}
```

**budget-notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  }
]
```

#### 1.2 Enable Cost Anomaly Detection
1. Go to **AWS Console** → **Cost Management** → **Cost Anomaly Detection**
2. Click **Create monitor**
3. Select **AWS Services** → **Amazon Bedrock**
4. Set alert threshold: $10
5. Add email notification

#### 1.3 Set Up CloudWatch Alarm for Invocations
```bash
# Alert when daily invocations exceed threshold
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-high-usage \
  --alarm-description "Alert when Bedrock invocations exceed 100/day" \
  --metric-name Invocations \
  --namespace AWS/Bedrock \
  --statistic Sum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:your-sns-topic
```

---

### Step 2: Track Token Usage

#### 2.1 Enable Detailed CloudWatch Logging
```bash
# When creating agent, enable logging
aws bedrock-agent create-agent \
  --agent-name MyAgent \
  --foundation-model anthropic.claude-3-haiku-20240307-v1:0 \
  --instruction "Your instructions here" \
  --agent-resource-role-arn YOUR_ROLE_ARN \
  --customer-encryption-key-arn YOUR_KMS_KEY \
  --idle-session-ttl-in-seconds 600
```

#### 2.2 Create Token Usage Dashboard
```python
# Script to analyze token usage from logs
import boto3
import json
from datetime import datetime, timedelta

logs_client = boto3.client('logs')

def analyze_token_usage(log_group, days=7):
    query = """
    fields @timestamp, @message
    | filter @message like /tokens/
    | stats sum(inputTokens) as totalInput, sum(outputTokens) as totalOutput
    """

    start_time = int((datetime.now() - timedelta(days=days)).timestamp())
    end_time = int(datetime.now().timestamp())

    response = logs_client.start_query(
        logGroupName=log_group,
        startTime=start_time,
        endTime=end_time,
        queryString=query
    )

    # Wait for query to complete and fetch results
    # Calculate costs based on model pricing

    return results

# Run weekly to track costs
results = analyze_token_usage('/aws/bedrock/agents/YOUR_AGENT_ID', days=7)
print(f"Estimated weekly cost: ${results['estimated_cost']:.2f}")
```

---

### Step 3: Implement Usage Limits (Application Level)

```python
# Example: Rate limiting in your application
from datetime import datetime
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_rate_limit(user_id, max_requests_per_day=10):
    key = f"bedrock:ratelimit:{user_id}:{datetime.now().date()}"
    current = redis_client.get(key)

    if current and int(current) >= max_requests_per_day:
        raise Exception("Daily rate limit exceeded")

    redis_client.incr(key)
    redis_client.expire(key, 86400)  # 24 hours

def invoke_agent_with_limit(prompt, user_id):
    check_rate_limit(user_id, max_requests_per_day=10)
    return invoke_agent(prompt)
```

---

## Minimal Cost Architecture

### Architecture 1: Absolute Minimum (No Knowledge Base)

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Your Application   │
│  (Rate Limited)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Bedrock Agent      │ ◄── Claude 3 Haiku (cheapest model)
│  - No Knowledge Base│
│  - 1-2 Action Groups│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  AWS Lambda         │ ◄── FREE (1M requests/month)
│  (Action Groups)    │
└─────────────────────┘

Estimated Monthly Cost: $5-15
```

**Components:**
- ✅ Bedrock Agent with Claude 3 Haiku
- ✅ 1-2 Lambda functions (action groups)
- ✅ CloudWatch Logs (7-day retention)
- ❌ No Knowledge Base (skip OpenSearch)
- ❌ No S3 (or minimal, < 1 GB)

**Use Cases:**
- Simple chatbots
- Task automation
- API orchestration
- Data retrieval from databases

---

### Architecture 2: Low Cost with Simple RAG (No OpenSearch)

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Your Application   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Bedrock Agent      │ ◄── Claude 3 Haiku
└──────┬──────────────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌─────────────┐    ┌─────────────────┐
│  Lambda     │    │  Lambda         │ ◄── Simple RAG
│  (Actions)  │    │  (Doc Search)   │     (No OpenSearch)
└─────────────┘    └────┬────────────┘
                        │
                        ▼
                   ┌─────────────┐
                   │  S3 Bucket  │ ◄── FREE (< 5GB)
                   │  (Docs +    │
                   │  Embeddings)│
                   └─────────────┘

Estimated Monthly Cost: $5-20
```

**Implementation:**
```python
# Lambda function for simple RAG
import json
import boto3
import numpy as np
from sentence_transformers import SentenceTransformer

s3 = boto3.client('s3')
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model

def lambda_handler(event, context):
    query = event['query']

    # Download embeddings from S3 (cached locally)
    embeddings = json.loads(s3.get_object(
        Bucket='my-kb-bucket',
        Key='embeddings.json'
    )['Body'].read())

    # Compute query embedding
    query_emb = model.encode(query)

    # Simple cosine similarity search
    similarities = [
        (doc['text'], cosine_similarity(query_emb, doc['embedding']))
        for doc in embeddings
    ]

    # Return top 3 results
    top_results = sorted(similarities, key=lambda x: x[1], reverse=True)[:3]

    return {
        'results': [{'text': r[0], 'score': r[1]} for r in top_results]
    }
```

**Limitations:**
- Works for < 10,000 documents
- Slower than OpenSearch (but still < 3 seconds)
- No advanced vector search features

---

### Architecture 3: Production-Ready (With Knowledge Base)

```
Only use this when budget allows $350+/month

┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Your Application   │
└──────┬──────────────┘
       │
       ▼
┌──────────────────────────────┐
│  Bedrock Agent               │ ◄── Claude 3 Sonnet
│  + Knowledge Base            │
└──────┬───────────────────────┘
       │
       ├───────────────┬────────────────┐
       ▼               ▼                ▼
┌─────────┐   ┌─────────────┐  ┌──────────────────┐
│ Lambda  │   │ S3 Bucket   │  │ OpenSearch       │
│ Actions │   │ (Docs)      │  │ Serverless       │
│         │   │             │  │ (Vector DB)      │
└─────────┘   └─────────────┘  └──────────────────┘

Estimated Monthly Cost: $350-500+
```

---

## Budget-Friendly Best Practices

### 1. Use Claude 3 Haiku for Development
```bash
# Always start with Haiku
aws bedrock-agent create-agent \
  --foundation-model anthropic.claude-3-haiku-20240307-v1:0 \
  ...

# Only upgrade to Sonnet for production if needed
```

### 2. Minimize Agent Instructions
```
❌ BAD (Long Instructions = More Tokens):
"You are a highly sophisticated customer service agent with extensive knowledge
of our products, services, policies, and procedures. You should always be polite,
professional, and helpful. When users ask questions, you should..."

✅ GOOD (Concise = Fewer Tokens):
"You are a customer service agent. Be helpful and professional. Use the
available tools to answer questions about orders and products."
```

### 3. Implement Caching
```python
# Cache common responses
import functools
from datetime import timedelta

@functools.lru_cache(maxsize=128)
def get_cached_response(prompt_hash):
    # Return cached response if available
    # Reduces Bedrock invocations
    pass

def invoke_agent_with_cache(prompt, ttl=3600):
    cache_key = hash(prompt)

    # Check cache first
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    # If not cached, invoke agent
    response = invoke_agent(prompt)

    # Cache for future use
    cache_response(cache_key, response, ttl)

    return response
```

### 4. Set Short Session Timeouts
```bash
# Don't keep sessions alive unnecessarily
# Shorter timeout = less potential for accidental usage

aws bedrock-agent update-agent \
  --agent-id YOUR_AGENT_ID \
  --idle-session-ttl-in-seconds 600  # 10 minutes (not 1 hour)
```

### 5. Disable Agent When Not Testing
```bash
# Disable agent to prevent accidental invocations
aws bedrock-agent update-agent \
  --agent-id YOUR_AGENT_ID \
  --agent-status DISABLED

# Re-enable only when testing
aws bedrock-agent update-agent \
  --agent-id YOUR_AGENT_ID \
  --agent-status ENABLED
```

### 6. Use Test Mode Wisely
```python
# Limit test invocations per day
MAX_DAILY_TESTS = 20

def run_test(test_cases):
    if get_daily_test_count() >= MAX_DAILY_TESTS:
        print("Daily test limit reached. Pausing until tomorrow.")
        return

    for test in test_cases:
        invoke_agent(test['prompt'])
        increment_test_count()
```

### 7. Monitor and Review Weekly
```bash
# Create weekly cost report
# Run this every Monday

#!/bin/bash
# weekly-cost-report.sh

echo "=== Weekly AWS Bedrock Cost Report ==="
echo "Period: $(date -d '7 days ago' +%Y-%m-%d) to $(date +%Y-%m-%d)"
echo ""

# Get costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '7 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --filter file://bedrock-filter.json | \
  jq -r '.ResultsByTime[] | "\(.TimePeriod.Start): $\(.Total.UnblendedCost.Amount)"'

echo ""
echo "If costs exceed $10/week, consider:"
echo "1. Reducing test frequency"
echo "2. Using shorter prompts"
echo "3. Switching to Claude Haiku"
```

---

## Summary: Recommended Free Tier Strategy

### Phase 1: Initial Testing ($5-15/month)
```
✅ Use: Claude 3 Haiku
✅ Use: Lambda for action groups (FREE)
✅ Use: Minimal S3 storage (FREE for 12 months)
✅ Use: CloudWatch Logs with 7-day retention (FREE)
❌ Skip: Knowledge Bases / OpenSearch ($350/month)
❌ Skip: Kendra ($810/month)
```

### Phase 2: Adding Document Search ($5-20/month)
```
✅ Use: Simple Lambda-based RAG (FREE tier covers most usage)
✅ Use: S3 for document + embedding storage (< $1/month)
✅ Use: sentence-transformers for embeddings (runs in Lambda)
❌ Skip: OpenSearch Serverless (still too expensive)
```

### Phase 3: Production (When Budget Allows)
```
✅ Upgrade: Claude 3 Sonnet (if quality demands it)
✅ Add: OpenSearch Serverless Knowledge Base ($350+/month)
✅ Add: Reserved capacity (if high volume)
✅ Add: Advanced monitoring and alerting
```

---

## Quick Reference: Cost Checklist

**Before creating any AWS resource:**
- [ ] Is this component free tier eligible?
- [ ] What's the minimum cost if not free?
- [ ] Can I use a cheaper alternative?
- [ ] Have I set up billing alerts?
- [ ] Can I test locally first?

**Weekly Review:**
- [ ] Check AWS Cost Explorer
- [ ] Review CloudWatch metrics
- [ ] Verify billing alerts are working
- [ ] Confirm no unexpected charges
- [ ] Disable unused resources

**Monthly Actions:**
- [ ] Review total costs vs budget
- [ ] Identify cost optimization opportunities
- [ ] Clean up old S3 objects/logs
- [ ] Review and adjust budgets if needed

---

## Additional Resources

- [AWS Free Tier Details](https://aws.amazon.com/free/)
- [AWS Pricing Calculator](https://calculator.aws/)
- [Bedrock Pricing Page](https://aws.amazon.com/bedrock/pricing/)
- [AWS Cost Management Best Practices](https://aws.amazon.com/aws-cost-management/aws-cost-optimization/)

---

## Conclusion

**Key Takeaways:**

1. **Bedrock is NOT free** - Minimum $5-15/month for basic testing
2. **OpenSearch/Knowledge Bases are EXPENSIVE** - $350+/month minimum
3. **Lambda, S3, CloudWatch are FREE** (within generous limits)
4. **Start simple** - Test without knowledge bases first
5. **Monitor religiously** - Set up billing alerts before deploying anything
6. **Use Claude Haiku** - 12x cheaper than Sonnet for testing

**You CAN build and test Bedrock Agents affordably, but you cannot run them at zero cost.**

The recommended approach: Start with Architecture 1 (Minimum $5-15/month), and only add expensive components when your use case justifies the cost.
