# AWS Cost Audit & Cleanup Guide
**Date**: 2026-03-26
**Status**: Student Account — No commercial use
**Goal**: Identify and safely remove all AWS resources to prevent billing surprise

---

## ⚠️ CRITICAL SECURITY NOTE

**DO NOT share AWS credentials with Claude or any AI system.**
Instead, you will use AWS CLI commands with your own locally-configured credentials.

---

## 📊 Current AWS Infrastructure Inventory

### ✅ **Infrastructure Defined in Code** (Terraform — Garmin Project)

All resources are defined in `/01-personal/garmin-health/backend/terraform/`

#### **1. Lambda Functions (4 total)**
- `garmin-integration-webhook-handler-dev`
  - Runtime: Python 3.11
  - Memory: 256 MB
  - Timeout: 30 sec
  - **Cost driver**: Invocations (1M free/month, then $0.20/M)

- `garmin-integration-fetch-activity-dev`
  - Runtime: Python 3.11
  - Memory: 512 MB
  - Timeout: 60 sec
  - **Cost driver**: Invocations + memory usage

- `garmin-integration-ai-analyzer-dev`
  - Runtime: Python 3.11
  - Memory: 512 MB (configurable, default)
  - Timeout: 300 sec
  - **IMPORTANT**: Calls AWS Bedrock (`bedrock:InvokeModel` IAM permission)
  - **Cost driver**: Bedrock model invocations (most expensive!)

- `garmin-integration-oauth-handler-dev`
  - Runtime: Python 3.11
  - Memory: 256 MB
  - Timeout: 30 sec
  - **Cost driver**: Invocations

#### **2. DynamoDB Tables (2 total)**
- `garmin-integration-activities-dev`
  - Hash key: `activity_id`
  - Global Secondary Index: `user-timestamp-index`
  - **Billing**: PAY_PER_REQUEST (on-demand)
  - **Cost drivers**: Write units + read units (free tier: 25 WCU, 25 RCU/month)
  - Features: Point-in-time recovery, encryption, TTL

- `garmin-integration-user-tokens-dev`
  - Hash key: `user_token`
  - Global Secondary Index: `user-id-index`
  - **Billing**: PAY_PER_REQUEST (on-demand)
  - **Cost drivers**: Write units + read units
  - Features: Point-in-time recovery, encryption, TTL

#### **3. API Gateway (REST API)**
- `garmin-integration-api-dev`
- **Endpoints**:
  - POST `/webhook` → webhook handler Lambda
  - POST `/oauth/initiate` → OAuth handler Lambda
  - GET `/oauth/callback` → OAuth handler Lambda
  - GET `/health` → mock response (free)
- **Billing**: $3.50/M per API + $0.35/M per 1M requests
- **Stage**: `prod` (configured)

#### **4. EventBridge (CloudWatch Events)**
- `garmin-integration-new-activity-dev` — triggers fetch-activity Lambda
- `garmin-integration-activity-data-ready-dev` — triggers ai-analyzer Lambda
- **Billing**: Free (first 5 custom rules, then per rule + per invocation)

#### **5. SQS Queue (Dead Letter Queue)**
- `garmin-integration-eventbridge-dlq-dev`
- **Billing**: Free tier: 1M requests/month
- **Cost**: ~$0.40 per M requests (after free tier)

#### **6. CloudWatch Logs** (auto-created)
- `/aws/lambda/garmin-integration-webhook-handler-dev` — 30-day retention
- `/aws/lambda/garmin-integration-fetch-activity-dev` — 30-day retention
- `/aws/lambda/garmin-integration-ai-analyzer-dev` — 30-day retention
- `/aws/lambda/garmin-integration-oauth-handler-dev` — 30-day retention
- `/aws/apigateway/garmin-integration-dev` — 30-day retention
- **Billing**: $0.50/GB ingested + $0.03/GB stored

#### **7. Secrets Manager**
- `garmin-integration-garmin-credentials-dev`
- Stores: Garmin OAuth consumer key + secret
- **Billing**: $0.40/secret/month

#### **8. IAM Roles & Policies (5 total)**
- 5 Lambda execution roles (webhook, fetch, analyzer, OAuth, EventBridge)
- Inline policies + managed policies (AWSLambdaBasicExecutionRole)
- **Billing**: FREE (IAM itself is free, only Bedrock calls cost)

#### **9. Lambda Layers**
- `garmin-integration-dependencies-dev`
- Contains: requests, requests-oauthlib, boto3
- **Billing**: FREE (included in Lambda compute)

#### **10. Optional: AWS X-Ray Tracing**
- `enable_xray_tracing = true` (in variables.tf)
- **Billing**: $0.50 per 1M trace records

---

## 💰 Monthly Cost Estimate (Actual Usage)

### Assumptions
- **Webhook calls**: 0 (no Garmin integration actually running)
- **Lambda invocations**: 0 (no webhook activity)
- **DynamoDB**: No reads/writes (free tier: 25 WCU, 25 RCU/month)
- **API Gateway**: No traffic

### Estimated Monthly Cost: **$0.70 — $1.40 USD**

| Component | Unit | Quantity | Cost |
|-----------|------|----------|------|
| Lambda | 1M invocations | 0 | $0 |
| DynamoDB | on-demand | ~0 usage | $0 |
| API Gateway | per API/month | 1 API | $3.50 |
| API requests | per 1M | 0 | $0 |
| Secrets Manager | per secret/month | 1 | $0.40 |
| CloudWatch Logs | per GB | ~0.05 GB | $0.03 |
| **TOTAL** | | | **$3.93/month** |

### **⚠️ MAJOR COST DRIVER: Bedrock Model Invocations**

If the `ai_analyzer` Lambda is actually calling Claude via Bedrock:
- **Claude 3.5 Sonnet pricing** (via Bedrock):
  - Input: $3/M tokens
  - Output: $15/M tokens
- **10 calls × 1K input tokens + 500 output tokens = $35-$40/month**
- **100 calls = $350-$400/month** ← Could add up quickly!

**Check your Bedrock usage**:
```bash
aws bedrock list-foundation-models --region us-east-1
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name ModelInvocations \
  --start-time 2026-03-01T00:00:00Z \
  --end-time 2026-03-26T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

---

## 🔍 Verification Commands

Run these AWS CLI commands **with your own AWS credentials** to verify what's actually deployed:

### **List Lambda Functions**
```bash
aws lambda list-functions \
  --region us-east-1 \
  --query 'Functions[?starts_with(FunctionName, `garmin`)]' \
  --output table
```

### **List DynamoDB Tables**
```bash
aws dynamodb list-tables \
  --region us-east-1 \
  --output table
```

### **List API Gateways**
```bash
aws apigateway get-rest-apis \
  --region us-east-1 \
  --query 'items[?starts_with(name, `garmin`)]' \
  --output table
```

### **List Secrets Manager Secrets**
```bash
aws secretsmanager list-secrets \
  --region us-east-1 \
  --filters Key=name,Values=garmin \
  --output table
```

### **Check CloudWatch Logs Storage**
```bash
aws logs describe-log-groups \
  --region us-east-1 \
  --query 'logGroups[?contains(logGroupName, `garmin`)]' \
  --output table
```

### **Check Billing Dashboard (Last 30 Days)**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-02-24,End=2026-03-26 \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["AWS Lambda","Amazon DynamoDB","API Gateway","AWS Secrets Manager"]}}' \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output table
```

---

## 🗑️ Safe Cleanup Procedure

### **Option 1: Destroy All Infrastructure (Recommended for Student Account)**

If you want to **completely remove everything**:

```bash
cd 01-personal/garmin-health/backend

# 1. Plan what will be deleted
terraform plan -destroy

# 2. Actually delete (this cannot be undone!)
terraform destroy

# Answer "yes" when prompted
```

**What this deletes**:
- ✅ All 4 Lambda functions
- ✅ Both DynamoDB tables (with point-in-time recovery snapshots)
- ✅ API Gateway REST API
- ✅ EventBridge rules
- ✅ SQS DLQ
- ✅ IAM roles and policies
- ✅ CloudWatch log groups
- ✅ Secrets Manager secret

**What it does NOT delete**:
- ❌ X-Ray trace data (if enabled) — manually delete via Console
- ❌ CloudWatch Alarms — manually delete via Console

**Estimated cost savings**: **$3.93/month** ✓

---

### **Option 2: Partial Cleanup (Keep some parts)**

If you want to keep the code but remove only the most expensive resources:

#### **Remove AI Analyzer Lambda (biggest cost if used)**
```bash
cd 01-personal/garmin-health/backend
# Edit terraform/lambda.tf, comment out:
#   - resource "aws_lambda_function" "ai_analyzer"
#   - resource "aws_cloudwatch_log_group" "ai_analyzer"
#   - outputs for ai_analyzer

terraform apply
```

#### **Remove API Gateway (costs $3.50/month even if unused)**
```bash
cd 01-personal/garmin-health/backend
# Edit terraform/api_gateway.tf, comment out all resources
terraform apply
```

#### **Remove Secrets Manager Secret ($0.40/month)**
```bash
cd 01-personal/garmin-health/backend
# Edit terraform/secrets.tf, comment out:
#   - resource "aws_secretsmanager_secret"
#   - resource "aws_secretsmanager_secret_version"

terraform apply
```

---

### **Option 3: Manual Cleanup (via AWS Console)**

If Terraform state is lost or corrupted:

1. **AWS Console** → **Lambda** → Delete functions starting with `garmin-`
2. **AWS Console** → **DynamoDB** → Delete tables starting with `garmin-`
3. **AWS Console** → **API Gateway** → Delete REST API named `garmin-*`
4. **AWS Console** → **Secrets Manager** → Delete secret `garmin-*`
5. **AWS Console** → **CloudWatch** → Log Groups → Delete groups starting with `/aws/lambda/garmin-*`
6. **AWS Console** → **IAM** → Roles → Delete roles starting with `garmin-*`

---

## ⚡ Additional AWS Resources to Check

### **AWS Bedrock (Potential hidden costs)**

If you ever created a Bedrock agent (separate from Lambda invocations):

```bash
# List Bedrock agents
aws bedrock list-agents \
  --region us-east-1

# List knowledge bases (RAG)
aws bedrock-agent list-knowledge-bases \
  --region us-east-1

# Check Bedrock model invocation usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name ModelInvocations \
  --start-time 2026-02-24T00:00:00Z \
  --end-time 2026-03-26T23:59:59Z \
  --period 3600 \
  --statistics Sum \
  --region us-east-1
```

### **S3 Buckets (often forgotten)**

```bash
aws s3 ls
```

### **VPC & Network Resources (can incur data transfer charges)**

```bash
aws ec2 describe-vpcs
aws ec2 describe-nat-gateways  # Expensive!
```

### **RDS, ElastiCache, etc.**

```bash
aws rds describe-db-instances
aws elasticache describe-cache-clusters
```

---

## 📋 Pre-Cleanup Checklist

Before running `terraform destroy`:

- [ ] Backed up DynamoDB data (if needed)
  ```bash
  aws dynamodb export-table-to-point-in-time \
    --table-arn "arn:aws:dynamodb:us-east-1:ACCOUNT_ID:table/garmin-integration-activities-dev" \
    --s3-bucket "my-backup-bucket" \
    --s3-prefix "garmin-backup/"
  ```

- [ ] Exported CloudWatch logs (if needed)
  ```bash
  aws logs create-export-task \
    --log-group-name "/aws/lambda/garmin-integration-webhook-handler-dev" \
    --from 1704067200000 \
    --to 1711324800000 \
    --destination "my-backup-bucket" \
    --destination-prefix "logs/"
  ```

- [ ] Saved Secrets Manager secret value (if you need those credentials elsewhere)
  ```bash
  aws secretsmanager get-secret-value \
    --secret-id "garmin-integration-garmin-credentials-dev" \
    > garmin-credentials-backup.json
  ```

- [ ] Verified no production traffic depends on this infrastructure (it's dev, so should be safe)

---

## ✅ Post-Cleanup Verification

After cleanup, verify everything is gone:

```bash
# Should return empty results
aws lambda list-functions --region us-east-1 --query 'Functions[?starts_with(FunctionName, `garmin`)]'
aws dynamodb list-tables --region us-east-1 | grep garmin
aws apigateway get-rest-apis --region us-east-1 | grep garmin
aws secretsmanager list-secrets --filters Key=name,Values=garmin | grep garmin

# Check Terraform state
cd 01-personal/garmin-health/backend
terraform state list  # Should show few/no garmin-* resources
```

---

## 🎯 Next Steps (Recommendations)

1. **Run verification commands** to see actual AWS state
2. **Check billing dashboard** for last 30 days of usage
3. **Check Bedrock usage** (most likely cost driver if Lambda called it)
4. **Decide**: Keep infrastructure or destroy?
5. **If destroying**: Run `terraform destroy` and verify cleanup
6. **If keeping**: Monitor costs monthly and set billing alerts:
   ```bash
   # Create billing alarm for $5/month
   aws cloudwatch put-metric-alarm \
     --alarm-name "AWS-Monthly-Cost-Alarm" \
     --alarm-description "Alert if monthly AWS spend exceeds $5" \
     --metric-name EstimatedCharges \
     --namespace AWS/Billing \
     --statistic Maximum \
     --period 86400 \
     --evaluation-periods 1 \
     --threshold 5 \
     --comparison-operator GreaterThanThreshold
   ```

---

## 📞 Get Help

**Important**: Do NOT share AWS credentials or secret keys with anyone.

To investigate costs further:
1. Go to AWS Console → **Billing Dashboard**
2. Select **Cost Explorer**
3. Filter by service, date range, resource tags
4. Look for unexpected charges

**If you need AWS CLI help**:
```bash
aws help
aws <service> help  # e.g., aws lambda help
```

---

**Last Updated**: 2026-03-26
**Reviewed by**: Claude Code Security Audit
**Status**: Ready for cleanup ✓
