# AWS Free Tier Cost Management & Budget Investigation Guide

## Overview
This guide helps you investigate unexpected AWS charges, identify expensive resources, and optimize costs when building AWS Bedrock Agents on the Free Tier.

---

## Table of Contents
1. [Investigating Budget Consumption](#investigating-budget-consumption)
2. [Common Cost Culprits for Bedrock Agents](#common-cost-culprits-for-bedrock-agents)
3. [Resource Cleanup Checklist](#resource-cleanup-checklist)
4. [Free Tier Optimization Strategies](#free-tier-optimization-strategies)
5. [Cost-Effective Testing Practices](#cost-effective-testing-practices)
6. [Setting Up Alerts](#setting-up-alerts)

---

## Investigating Budget Consumption

### Step 1: Access AWS Cost Explorer

**Via AWS Console:**
```
1. Log into AWS Console
2. Click on your account name (top right) → "Billing and Cost Management"
3. In left sidebar, click "Cost Explorer"
4. Click "Launch Cost Explorer" (if first time)
```

**What to Look For:**
- Daily cost breakdown
- Service-by-service costs
- Sudden spikes in specific services

**Tasks:**
- [ ] Navigate to Cost Explorer
- [ ] Select time range: Last 7 days or Last 30 days
- [ ] Group by: Service
- [ ] Identify which service has highest costs

### Step 2: Analyze Costs by Service

**Top Cost Drill-Down:**
```
1. In Cost Explorer, set Group by: "Service"
2. Click on the highest cost service
3. Change Group by: "Usage Type"
4. This shows exactly what you're being charged for
```

**Common AWS Bedrock Cost Categories:**
- **Bedrock Model Invocation**: Pay per input/output token
- **Bedrock Knowledge Base**: OpenSearch Serverless, S3 storage, vector embeddings
- **Lambda Invocations**: Function executions and duration
- **S3 Storage**: Data storage and requests
- **CloudWatch Logs**: Log ingestion and storage
- **Data Transfer**: Outbound data transfer

### Step 3: Check Billing Dashboard for Details

**Via AWS Console:**
```
1. Billing and Cost Management → Bills
2. Select current month
3. Expand each service to see detailed charges
4. Look for "Usage Quantity" column
```

**Key Metrics to Check:**
- **Bedrock**: Number of tokens processed
- **OpenSearch Serverless**: OCU (OpenSearch Compute Units) hours
- **Lambda**: Number of requests and GB-seconds
- **S3**: Storage amount and API requests

**Tasks:**
- [ ] Review detailed bill line items
- [ ] Note which resources have unexpected charges
- [ ] Calculate per-action costs

### Step 4: Use AWS Cost and Usage Reports

**Create Detailed Cost Report:**
```bash
# Using AWS CLI to get cost and usage data
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-05 \
  --granularity DAILY \
  --metrics "UnblendedCost" "UsageQuantity" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1
```

**Tasks:**
- [ ] Run cost report for the past week
- [ ] Export to CSV for analysis
- [ ] Identify cost trends and spikes

### Step 5: Check CloudWatch Metrics for Usage Patterns

**For Bedrock Agents:**
```bash
# Check agent invocation count
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name Invocations \
  --dimensions Name=AgentId,Value=YOUR_AGENT_ID \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-05T00:00:00Z \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

**For Lambda Functions:**
```bash
# Check Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=YOUR_FUNCTION_NAME \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-05T00:00:00Z \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

**Tasks:**
- [ ] Check invocation counts for all agents
- [ ] Identify any runaway processes
- [ ] Look for unexpected activity patterns

---

## Common Cost Culprits for Bedrock Agents

### 1. OpenSearch Serverless (Knowledge Base Backend)
**Why It's Expensive:**
- Charges per OCU-hour (OpenSearch Compute Unit)
- **Minimum 2 OCUs for data ingestion** (~$0.24/hour = ~$175/month)
- **Minimum 2 OCUs for search** (~$0.24/hour = ~$175/month)
- Total minimum: **~$350/month** if knowledge base is running

**How to Check:**
```bash
# List all OpenSearch Serverless collections
aws opensearchserverless list-collections --region us-east-1

# Get collection details
aws opensearchserverless batch-get-collection \
  --ids YOUR_COLLECTION_ID \
  --region us-east-1
```

**Cost Impact:**
- ⚠️ **HIGHEST COST DRIVER** for Bedrock Agents
- Runs continuously once created
- NOT covered by Free Tier

### 2. Bedrock Model Inference Costs
**Pricing per Model (as of 2026):**

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| Claude 3 Sonnet | ~$0.003 | ~$0.015 |
| Claude 3 Haiku | ~$0.00025 | ~$0.00125 |
| Titan Text Lite | ~$0.0003 | ~$0.0004 |

**How to Check Token Usage:**
```bash
# This data is in CloudWatch Logs for your agent
aws logs tail /aws/bedrock/agents/YOUR_AGENT_ID \
  --since 1h \
  --format short \
  --region us-east-1
```

**Cost Impact:**
- Moderate, depends on usage
- Can add up quickly with testing
- NOT covered by Free Tier

### 3. Embeddings Generation (Knowledge Base)
**Why It's Expensive:**
- Charged per text chunk embedded
- Titan Embeddings: ~$0.0001 per 1K tokens
- One-time cost during knowledge base sync
- Repeats if you update documents

**How to Check:**
```bash
# Check S3 bucket size (documents being embedded)
aws s3 ls s3://your-kb-bucket --recursive --summarize --human-readable
```

**Cost Impact:**
- One-time or infrequent
- Can be significant for large document sets
- NOT covered by Free Tier

### 4. S3 Storage and Requests
**Free Tier Limits:**
- ✅ 5 GB storage (first 12 months)
- ✅ 20,000 GET requests
- ✅ 2,000 PUT requests

**How to Check:**
```bash
# List all S3 buckets with creation date
aws s3api list-buckets --query 'Buckets[*].[Name,CreationDate]' --output table

# Get bucket size
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name BucketSizeBytes \
  --dimensions Name=BucketName,Value=YOUR_BUCKET_NAME Name=StorageType,Value=StandardStorage \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-05T00:00:00Z \
  --period 86400 \
  --statistics Average \
  --region us-east-1
```

**Cost Impact:**
- Usually minimal
- Mostly covered by Free Tier
- Watch for excessive API requests

### 5. Lambda Function Execution
**Free Tier Limits:**
- ✅ 1 million requests per month (always free)
- ✅ 400,000 GB-seconds of compute time

**How to Check:**
```bash
# List all Lambda functions
aws lambda list-functions --query 'Functions[*].[FunctionName,Runtime,LastModified]' --output table

# Get function metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=YOUR_FUNCTION \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-05T00:00:00Z \
  --period 86400 \
  --statistics Sum \
  --region us-east-1
```

**Cost Impact:**
- Usually minimal with normal testing
- Mostly covered by Free Tier
- Watch for runaway invocations

### 6. CloudWatch Logs
**Free Tier Limits:**
- ✅ 5 GB ingestion
- ✅ 5 GB storage

**How to Check:**
```bash
# List all log groups with size
aws logs describe-log-groups \
  --query 'logGroups[*].[logGroupName,storedBytes]' \
  --output table \
  --region us-east-1

# Get specific log group size
aws logs describe-log-groups \
  --log-group-name-prefix /aws/bedrock \
  --region us-east-1
```

**Cost Impact:**
- Can accumulate with verbose logging
- Mostly covered by Free Tier
- Delete old logs regularly

### 7. Data Transfer Costs
**Free Tier Limits:**
- ✅ 100 GB outbound per month (first 12 months)

**How to Check:**
Via Cost Explorer:
```
1. Cost Explorer → Group by: Usage Type
2. Look for "DataTransfer-Out" charges
```

**Cost Impact:**
- Usually minimal for testing
- Mostly covered by Free Tier

---

## Resource Cleanup Checklist

### Critical: Delete OpenSearch Serverless Collections FIRST

**This is likely your biggest cost driver!**

```bash
# 1. List all collections
aws opensearchserverless list-collections --region us-east-1

# 2. Delete collection (replace with your collection ID)
aws opensearchserverless delete-collection \
  --id YOUR_COLLECTION_ID \
  --region us-east-1

# 3. Verify deletion
aws opensearchserverless list-collections --region us-east-1
```

**Tasks:**
- [ ] List all OpenSearch Serverless collections
- [ ] Delete collections you're not actively using
- [ ] Verify deletion completed
- [ ] **Expected savings: ~$350/month per collection**

### Delete or Disable Bedrock Agents

```bash
# List all agents
aws bedrock-agent list-agents --region us-east-1

# Delete agent
aws bedrock-agent delete-agent \
  --agent-id YOUR_AGENT_ID \
  --region us-east-1
```

**Tasks:**
- [ ] List all Bedrock agents
- [ ] Delete agents not in use
- [ ] Keep only one agent for active testing

### Delete Bedrock Knowledge Bases

```bash
# List knowledge bases
aws bedrock-agent list-knowledge-bases --region us-east-1

# Delete knowledge base
aws bedrock-agent delete-knowledge-base \
  --knowledge-base-id YOUR_KB_ID \
  --region us-east-1
```

**Note:** Deleting the knowledge base does NOT automatically delete the OpenSearch collection!

**Tasks:**
- [ ] List all knowledge bases
- [ ] Delete unused knowledge bases
- [ ] Separately delete associated OpenSearch collections

### Clean Up S3 Buckets

```bash
# List bucket contents
aws s3 ls s3://your-bucket-name --recursive

# Delete specific objects
aws s3 rm s3://your-bucket-name/path/to/file

# Empty entire bucket
aws s3 rm s3://your-bucket-name --recursive

# Delete bucket
aws s3 rb s3://your-bucket-name
```

**Tasks:**
- [ ] List all S3 buckets
- [ ] Delete test documents not needed
- [ ] Remove old bucket versions if versioning enabled
- [ ] Delete empty buckets

### Clean Up Lambda Functions

```bash
# List functions
aws lambda list-functions --region us-east-1

# Delete function
aws lambda delete-function \
  --function-name YOUR_FUNCTION_NAME \
  --region us-east-1
```

**Tasks:**
- [ ] List all Lambda functions
- [ ] Delete test/unused functions
- [ ] Keep only necessary action group functions

### Clean Up CloudWatch Logs

```bash
# List log groups
aws logs describe-log-groups --region us-east-1

# Delete log group
aws logs delete-log-group \
  --log-group-name /aws/bedrock/agents/YOUR_AGENT_ID \
  --region us-east-1

# Set retention policy (auto-delete after X days)
aws logs put-retention-policy \
  --log-group-name /aws/lambda/your-function \
  --retention-in-days 1 \
  --region us-east-1
```

**Tasks:**
- [ ] List all log groups
- [ ] Delete logs for deleted resources
- [ ] Set 1-day retention for test environments
- [ ] Set 3-7 day retention for active development

### Clean Up IAM Roles and Policies

```bash
# List roles
aws iam list-roles --query 'Roles[?contains(RoleName, `Bedrock`)].RoleName'

# Delete role (after detaching policies)
aws iam delete-role --role-name YourRoleName
```

**Tasks:**
- [ ] List all IAM roles
- [ ] Delete roles for deleted agents/functions
- [ ] Remove unused custom policies

---

## Free Tier Optimization Strategies

### Strategy 1: Avoid Knowledge Bases for Testing

**Problem:** OpenSearch Serverless costs ~$350/month minimum

**Solution:** Use simpler alternatives for learning

**Option A: Direct Prompt Context**
```python
# Instead of knowledge base, include context directly in prompt
context = """
Product Information:
- Product A: Description, price, features
- Product B: Description, price, features
"""

prompt = f"{context}\n\nUser question: {user_question}"
```

**Option B: Simple S3 + Lambda Retrieval**
```python
# Store documents in S3, retrieve in Lambda
import boto3
s3 = boto3.client('s3')

def get_context(topic):
    # Retrieve specific document from S3
    response = s3.get_object(Bucket='my-bucket', Key=f'{topic}.txt')
    return response['Body'].read().decode('utf-8')
```

**Benefits:**
- ✅ No OpenSearch costs
- ✅ S3 covered by Free Tier
- ✅ Lambda covered by Free Tier
- ⚠️ Less sophisticated retrieval
- ⚠️ Manual document selection needed

**Tasks:**
- [ ] Avoid creating knowledge bases until production
- [ ] Use prompt engineering for context instead
- [ ] Test with small, hard-coded contexts first

### Strategy 2: Use Cheaper Models

**Model Cost Comparison:**

| Model | Cost (per 1M tokens) | Use Case |
|-------|---------------------|----------|
| Claude 3 Opus | ~$15 (input) | Production, complex reasoning |
| **Claude 3 Sonnet** | ~$3 (input) | Balanced, good for most cases |
| **Claude 3 Haiku** | ~$0.25 (input) | ✅ **Testing, simple tasks** |
| Titan Text Lite | ~$0.30 (input) | ✅ **Basic text generation** |

**Recommendation:**
- Use **Claude 3 Haiku** for all testing and development
- Switch to Sonnet only for production
- Avoid Opus unless absolutely necessary

**How to Change:**
```bash
# Update agent to use Haiku
aws bedrock-agent update-agent \
  --agent-id YOUR_AGENT_ID \
  --foundation-model anthropic.claude-3-haiku-20240307-v1:0 \
  --agent-name "My Test Agent" \
  --agent-resource-role-arn YOUR_ROLE_ARN \
  --region us-east-1
```

**Tasks:**
- [ ] Change all agents to use Claude 3 Haiku
- [ ] Update in agent settings via console
- [ ] Re-prepare agent after changes

### Strategy 3: Minimize Token Usage

**Techniques:**

**1. Shorter Agent Instructions**
```
❌ BAD (verbose):
"You are a highly sophisticated customer service representative for our premium e-commerce platform. Your role is to assist customers with their inquiries regarding orders, products, shipping, returns, and account management. Always maintain a professional yet friendly tone. When customers ask questions, you should first check their order status using the appropriate action..."

✅ GOOD (concise):
"You assist customers with orders and products. Check order status when asked. Be helpful and brief."
```

**2. Limit Context Window**
- Keep action group descriptions short
- Don't include unnecessary examples
- Avoid redundant instructions

**3. Use Streaming Wisely**
- Don't re-invoke for small clarifications
- Batch questions when possible

**4. Test with Minimal Conversations**
- Use short test queries
- Avoid long multi-turn conversations during testing
- Plan your test cases to be efficient

**Tasks:**
- [ ] Reduce agent instructions to essentials
- [ ] Simplify action group schemas
- [ ] Plan efficient test scripts

### Strategy 4: Test Locally Before AWS

**Use Local Simulation:**

```python
# Test your Lambda functions locally
def lambda_handler(event, context):
    # Your code
    return response

# Local test
test_event = {
    'actionGroup': 'MyActions',
    'apiPath': '/getOrderStatus',
    'parameters': [{'name': 'order_id', 'value': '12345'}]
}

result = lambda_handler(test_event, None)
print(result)
```

**Benefits:**
- ✅ No AWS charges for local testing
- ✅ Faster iteration
- ✅ Debug before deploying

**Tools:**
- AWS SAM CLI for local Lambda testing
- LocalStack for AWS service simulation
- Bedrock SDK with local models (if available)

**Tasks:**
- [ ] Test Lambda functions locally first
- [ ] Validate logic before deploying to AWS
- [ ] Use print statements instead of CloudWatch logs locally

### Strategy 5: Use Free Tier Services Instead

**Alternatives to Bedrock (for learning):**

**Option A: OpenAI Free Tier**
- $5 free credits for new accounts
- Test agent logic with GPT-3.5
- Switch to Bedrock later

**Option B: Local LLMs**
- Ollama (free, local)
- LM Studio (free, local)
- Test conversation flow locally

**Option C: Mock Responses**
```python
# Mock agent responses for testing infrastructure
def mock_agent_response(prompt):
    if "order status" in prompt.lower():
        return {"status": "shipped", "tracking": "123456"}
    return {"message": "Understood"}

# Test your application logic
response = mock_agent_response("Check order status")
```

**When to Use:**
- ✅ Learning agent architecture
- ✅ Testing application integration
- ✅ Developing UI/UX
- ⚠️ Not for testing Bedrock-specific features

### Strategy 6: Set Hard Spending Limits

**Create Budget Alerts:**

```bash
# Create a budget with $5 limit
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**budget.json:**
```json
{
  "BudgetName": "BedrockTestingBudget",
  "BudgetLimit": {
    "Amount": "5",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

**notifications.json:**
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
  }
]
```

**Tasks:**
- [ ] Create monthly budget ($5-10)
- [ ] Set alerts at 50%, 80%, 100%
- [ ] Review alerts immediately when received

---

## Cost-Effective Testing Practices

### Practice 1: Test Planning

**Before Each Test Session:**
```
1. Write down specific test cases
2. Estimate tokens needed
3. Plan shortest path to validate
4. Set session time limit (e.g., 15 minutes)
```

**Example Test Plan:**
```markdown
## Test Session 1: Basic Agent Response
Duration: 10 minutes
Expected Cost: $0.10

Test Cases:
1. "Hello" → Verify greeting
2. "What can you do?" → Verify capabilities listed
3. "Check order 12345" → Verify action group called

Stop Criteria: All 3 tests pass OR 10 minutes elapsed
```

### Practice 2: Batch Testing

**Instead of:**
```
Test 1: "Hello"
Wait... check response
Test 2: "What's my order status?"
Wait... check response
Test 3: "Can you help me?"
```

**Do This:**
```python
# Batch test script
test_cases = [
    "Hello",
    "What's my order status for 12345?",
    "Can you help me with a return?"
]

for i, test in enumerate(test_cases):
    print(f"\n--- Test {i+1} ---")
    response = invoke_agent(test, f"session-{i}")
    print(f"Response: {response}")
    # Log results to file
```

**Benefits:**
- Run all tests at once
- Easy to reproduce
- Track costs per batch
- Avoid forgotten test sessions

### Practice 3: Session Management

**Problem:** Leaving sessions open accumulates context

**Solution:**
```python
import uuid

def run_test(prompt):
    # Use unique session ID each time
    session_id = str(uuid.uuid4())
    response = invoke_agent(prompt, session_id)
    # Session ends after this call
    return response
```

**Benefits:**
- No accumulated conversation history
- Lower token usage
- Predictable costs

### Practice 4: Monitoring During Tests

**Create Simple Cost Tracker:**
```python
import boto3
from datetime import datetime, timedelta

def get_today_cost():
    ce = boto3.client('ce', region_name='us-east-1')

    end = datetime.now()
    start = end - timedelta(days=1)

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost']
    )

    cost = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    print(f"Cost today: ${float(cost):.2f}")
    return float(cost)

# Check before and after testing
print("Before tests:")
before = get_today_cost()

# Run your tests
run_my_tests()

print("\nAfter tests:")
after = get_today_cost()
print(f"Tests cost: ${after - before:.2f}")
```

### Practice 5: Use Agent Versioning

**Strategy:**
1. Create agent
2. Test thoroughly
3. Create version/alias
4. Delete test resources
5. Only recreate when needed

**Benefits:**
- Keep working configuration
- Avoid continuous resource usage
- Recreate from version when needed

---

## Setting Up Cost Alerts

### Alert 1: Daily Budget Threshold

**Using AWS Budgets:**

Via Console:
```
1. Billing Dashboard → Budgets → Create budget
2. Budget type: Cost budget
3. Period: Daily
4. Amount: $1.00
5. Alert threshold: $0.50 (50%)
6. Email: your-email@example.com
```

### Alert 2: Service-Specific Alerts

**For Bedrock:**
```bash
# Create CloudWatch alarm for daily Bedrock costs
aws cloudwatch put-metric-alarm \
  --alarm-name bedrock-daily-cost-alarm \
  --alarm-description "Alert when Bedrock costs exceed $2/day" \
  --namespace AWS/Billing \
  --metric-name EstimatedCharges \
  --dimensions Name=ServiceName,Value=AmazonBedrock \
  --statistic Maximum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 2.0 \
  --comparison-operator GreaterThanThreshold \
  --region us-east-1
```

### Alert 3: Anomaly Detection

**Enable AWS Cost Anomaly Detection:**

Via Console:
```
1. Billing Dashboard → Cost Anomaly Detection
2. Create monitor
3. Monitor type: AWS services
4. Alert preference: Email
5. Threshold: $1.00
```

**Benefits:**
- Automatically detects unusual spending
- Catches runaway processes
- No configuration needed

**Tasks:**
- [ ] Enable Cost Anomaly Detection
- [ ] Set up email notifications
- [ ] Review weekly reports

---

## Emergency Cost Control

### If Costs Are Running Away

**Immediate Actions (in order):**

**1. Delete OpenSearch Serverless Collections (FIRST!)**
```bash
aws opensearchserverless list-collections --region us-east-1
aws opensearchserverless delete-collection --id COLLECTION_ID --region us-east-1
```
**Impact:** Stops ~$350/month immediately

**2. Delete All Bedrock Agents**
```bash
aws bedrock-agent list-agents --region us-east-1
aws bedrock-agent delete-agent --agent-id AGENT_ID --region us-east-1
```

**3. Delete All Knowledge Bases**
```bash
aws bedrock-agent list-knowledge-bases --region us-east-1
aws bedrock-agent delete-knowledge-base --knowledge-base-id KB_ID --region us-east-1
```

**4. Stop All Lambda Functions**
```bash
# Delete all test Lambda functions
aws lambda list-functions --query 'Functions[*].FunctionName' --output text | \
  xargs -I {} aws lambda delete-function --function-name {}
```

**5. Check for Running Instances**
```bash
# List EC2 instances (should be none for Bedrock testing)
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table

# Terminate if any found
aws ec2 terminate-instances --instance-ids i-xxxxx
```

**6. Review All Regions**
```bash
# Check if resources in other regions
for region in us-east-1 us-west-2 eu-west-1; do
  echo "=== $region ==="
  aws bedrock-agent list-agents --region $region
done
```

### Verify All Resources Deleted

**Checklist:**
- [ ] OpenSearch Serverless: 0 collections
- [ ] Bedrock Agents: 0 agents
- [ ] Bedrock Knowledge Bases: 0 KBs
- [ ] Lambda Functions: Only essential ones
- [ ] S3 Buckets: Only necessary ones
- [ ] CloudWatch Log Groups: Set to 1-day retention
- [ ] EC2 Instances: 0 running
- [ ] All regions checked

---

## Recommended Free Tier Testing Approach

### Phase 1: Learn Without AWS (Week 1)
- [ ] Read Bedrock documentation
- [ ] Watch AWS tutorials
- [ ] Study OpenAPI schemas
- [ ] Plan your agent design
- [ ] Write Lambda function logic locally
- [ ] Test Lambda functions locally
- **Cost: $0**

### Phase 2: Minimal AWS Testing (Week 2)
- [ ] Create ONE simple agent (no knowledge base)
- [ ] Use Claude 3 Haiku model
- [ ] Add ONE action group with ONE Lambda
- [ ] Run 10-20 focused tests
- [ ] Delete agent immediately after
- **Estimated Cost: $0.50 - $2**

### Phase 3: Knowledge Base Testing (Week 3, Optional)
- [ ] Create knowledge base ONLY if needed
- [ ] Use SMALL document set (< 10 documents)
- [ ] Test for 1-2 hours only
- [ ] **DELETE OpenSearch collection same day**
- [ ] Document learnings
- **Estimated Cost: $5 - $10**

### Phase 4: Production Planning (Week 4)
- [ ] Design production architecture
- [ ] Calculate production costs
- [ ] Plan budget ($50-100/month)
- [ ] Implement cost controls
- **Cost: $0** (planning only)

---

## Cost Calculation Examples

### Scenario 1: Simple Agent Testing (No Knowledge Base)
```
Resources:
- 1 Bedrock Agent (Claude 3 Haiku)
- 2 Lambda functions
- 1 S3 bucket (< 1GB)
- CloudWatch logs (< 1GB)

Testing:
- 50 queries
- Average 500 input tokens, 200 output tokens per query

Cost Breakdown:
- Bedrock (Haiku): 50 * (500 * 0.00025 + 200 * 0.00125) / 1000 = $0.019
- Lambda: Free Tier (< 1M requests)
- S3: Free Tier
- CloudWatch: Free Tier

Total: ~$0.02
```

### Scenario 2: Agent with Knowledge Base (24 hours)
```
Resources:
- 1 Bedrock Agent (Claude 3 Haiku)
- 1 Knowledge Base (OpenSearch Serverless)
- 100 documents (10MB)
- S3 bucket
- CloudWatch logs

Testing:
- 50 queries with KB retrieval

Cost Breakdown:
- OpenSearch: 4 OCUs * 24 hours * $0.24/OCU-hour = $23.04
- Embeddings: 10MB * ~2500 tokens/MB * $0.0001/1K = $0.25
- Bedrock queries: ~$0.02
- S3: Free Tier
- Lambda: Free Tier
- CloudWatch: Free Tier

Total: ~$23.30 (for 24 hours)
```

**Key Insight:** Knowledge Base costs 1000x more than simple agent!

---

## Quick Reference Commands

### Check Current Costs
```bash
# Today's cost
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 day ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --region us-east-1
```

### List All Bedrock Resources
```bash
# Agents
aws bedrock-agent list-agents --region us-east-1

# Knowledge Bases
aws bedrock-agent list-knowledge-bases --region us-east-1

# OpenSearch collections (EXPENSIVE!)
aws opensearchserverless list-collections --region us-east-1
```

### Nuclear Option: Delete Everything
```bash
#!/bin/bash
# WARNING: This deletes ALL Bedrock resources!
REGION=us-east-1

# Delete all agents
aws bedrock-agent list-agents --region $REGION --query 'agentSummaries[*].agentId' --output text | \
  xargs -I {} aws bedrock-agent delete-agent --agent-id {} --region $REGION

# Delete all knowledge bases
aws bedrock-agent list-knowledge-bases --region $REGION --query 'knowledgeBaseSummaries[*].knowledgeBaseId' --output text | \
  xargs -I {} aws bedrock-agent delete-knowledge-base --knowledge-base-id {} --region $REGION

# Delete all OpenSearch collections
aws opensearchserverless list-collections --region $REGION --query 'collectionSummaries[*].id' --output text | \
  xargs -I {} aws opensearchserverless delete-collection --id {} --region $REGION

echo "All Bedrock resources deleted!"
```

---

## Summary: Action Plan for You

Based on your situation, here's what to do RIGHT NOW:

### Immediate (Next 30 Minutes):
1. [ ] Check Cost Explorer to identify top cost driver
2. [ ] Delete OpenSearch Serverless collections if any exist
3. [ ] Delete all Bedrock agents not actively testing
4. [ ] Delete all Bedrock knowledge bases
5. [ ] Set CloudWatch log retention to 1 day
6. [ ] Create $5 daily budget alert

### Short Term (This Week):
7. [ ] Review detailed billing for past charges
8. [ ] Learn which services caused the overspend
9. [ ] Read optimization strategies section above
10. [ ] Plan cost-effective testing approach
11. [ ] Test locally before deploying to AWS

### Ongoing:
12. [ ] Always use Claude 3 Haiku for testing
13. [ ] Avoid knowledge bases until production
14. [ ] Delete resources same day as testing
15. [ ] Check Cost Explorer daily during testing
16. [ ] Use batch test scripts instead of manual testing

---

## Additional Resources

### AWS Cost Management Tools:
- [AWS Cost Explorer](https://console.aws.amazon.com/cost-management/home#/cost-explorer)
- [AWS Budgets](https://console.aws.amazon.com/billing/home#/budgets)
- [AWS Cost Anomaly Detection](https://console.aws.amazon.com/cost-management/home#/anomaly-detection)
- [AWS Pricing Calculator](https://calculator.aws/)

### Bedrock Pricing:
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [OpenSearch Serverless Pricing](https://aws.amazon.com/opensearch-service/pricing/)

### Free Alternatives for Learning:
- [Ollama - Local LLMs](https://ollama.ai/)
- [LM Studio - Local Models](https://lmstudio.ai/)
- [OpenAI Playground](https://platform.openai.com/playground)

---

**Remember:** For Free Tier learning, avoid Knowledge Bases entirely and use Claude 3 Haiku for all testing!
