# AWS Cleanup Decision Guide
**For**: Student Account (No Commercial Use)
**Goal**: Avoid billing surprises by making an informed cleanup decision

---

## 🚦 Quick Decision Flow

```
                              START
                                ▼
                    Have you used the
                 Garmin AWS integration?
                      (webhook, OAuth, etc.)
                         /        \
                    YES/          \NO
                      /            \
                     ▼              ▼
            Check CloudWatch   Keep for now
            for Lambda          (costs ~$4/mo)
            invocations              ▼
              /      \         Monitor monthly
          YES        NO        Add billing alerts
            ▼         ▼              ▼
        Could    Definitely   DECISION: Teardown
        have     recommend    when ready
        costs    teardown
             ▼
        Evaluate actual
        Bedrock usage
        (most expensive!)
             ▼
        DECISION:
        Keep OR Destroy
```

---

## 📊 Decision Matrix

| Scenario | Monthly Cost | Recommendation | Next Step |
|----------|-------------|-----------------|-----------|
| **Never used Lambda/API** | ~$4 | ⚠️ **DESTROY** | Run `terraform destroy` |
| **Used Lambda <10x/month** | $4-5 | ⚠️ **DESTROY** | Check logs first, then destroy |
| **Used Lambda 10-100x/month** | $5-10 | ⚠️ **DESTROY** | Student account, no need for cloud |
| **Heavy Bedrock usage** | $50-500 | ⚠️ **DESTROY** | This is expensive! Remove AI analyzer |
| **Will use again later** | $4+ | ✅ **KEEP** | Set billing alerts + monitoring |

---

## 🔍 Step 1: Check Actual Usage (5 minutes)

**Prerequisite**: AWS CLI configured with your credentials

```bash
# First, run the audit script
cd 01-personal/garmin-health/backend
bash scripts/audit-aws.sh
```

This will show you exactly what's deployed.

---

## 📈 Step 2: Check Real Costs (AWS Console)

1. Go to **AWS Console** → **Billing Dashboard**
2. Click **Cost Explorer**
3. Set date range: **Last 30 days**
4. Filter by Services:
   - ✓ AWS Lambda
   - ✓ Amazon DynamoDB
   - ✓ API Gateway
   - ✓ Secrets Manager
   - ✓ AWS Bedrock ⚠️ (check this!)

**What you're looking for**:
- If all services show $0 → **SAFE TO DESTROY**
- If Bedrock shows charges → **HIGH PRIORITY TO DESTROY**
- If API Gateway shows charges → Normal ($3.50 base)

---

## 💻 Step 3: Check CloudWatch Logs for Evidence

**Did your Lambda functions actually run?**

```bash
# Check webhook handler logs
aws logs tail /aws/lambda/garmin-integration-webhook-handler-dev \
  --since 30d \
  --format short

# Check AI analyzer logs (most important!)
aws logs tail /aws/lambda/garmin-integration-ai-analyzer-dev \
  --since 30d \
  --format short
```

If no log entries in last 30 days → **Functions never ran → SAFE TO DESTROY**

---

## 🎯 Decision: Keep or Destroy

### ✅ **DESTROY IF:**
- [ ] Functions have no log entries (never called)
- [ ] Billing shows $0 for Lambda, DynamoDB, Bedrock
- [ ] Not actively using Garmin OAuth flow
- [ ] This is a student account (no production use)
- [ ] Don't plan to use this in next 6 months

### ⚠️ **KEEP IF:**
- [ ] Plan to use Garmin integration in near future
- [ ] Want to maintain OAuth tokens in DynamoDB
- [ ] Will integrate with Garmin API again
- [ ] Have production data to preserve

---

## 🗑️ Recommended Action: **DESTROY**

**Why?** For a student account with no active use:
- Infrastructure is sitting idle, costing ~$4/month
- Bedrock integration could silently rack up charges
- Can redeploy anytime from code (it's all in Terraform)
- Protects against bill shock

---

## 🚀 How to Destroy (Safe Procedure)

### **Step 1: Backup Data (Optional)**

If you want to preserve DynamoDB records:

```bash
cd 01-personal/garmin-health/backend

# Export activities table
aws dynamodb export-table-to-point-in-time \
  --table-arn "arn:aws:dynamodb:us-east-1:$(aws sts get-caller-identity --query Account --output text):table/garmin-integration-activities-dev" \
  --s3-bucket "my-backup-bucket" \
  --s3-prefix "garmin-backup/"

# Export user tokens table
aws dynamodb export-table-to-point-in-time \
  --table-arn "arn:aws:dynamodb:us-east-1:$(aws sts get-caller-identity --query Account --output text):table/garmin-integration-user-tokens-dev" \
  --s3-bucket "my-backup-bucket" \
  --s3-prefix "garmin-backup/"
```

### **Step 2: Plan What Will Be Deleted**

```bash
cd 01-personal/garmin-health/backend

# See everything that will be deleted (no changes made)
terraform plan -destroy
```

**Review the output carefully!** It should show:
- ✓ 4 Lambda functions
- ✓ 2 DynamoDB tables
- ✓ 1 API Gateway
- ✓ EventBridge rules
- ✓ SQS DLQ
- ✓ CloudWatch log groups
- ✓ IAM roles

### **Step 3: Actually Delete (POINT OF NO RETURN)**

```bash
cd 01-personal/garmin-health/backend

# Delete infrastructure
terraform destroy

# When prompted, type "yes" to confirm
```

**⚠️ This cannot be undone!** But your code stays, so you can redeploy later.

### **Step 4: Verify Everything's Gone**

```bash
# Run audit script again
bash scripts/audit-aws.sh

# Should show:
#   ✓ No Garmin Lambda functions found
#   ✓ No Garmin DynamoDB tables found
#   ✓ No Garmin API Gateways found
#   etc.
```

---

## 🛡️ What Happens After Destroy?

### You **KEEP**:
- ✅ All source code (Terraform, Lambda functions, etc.)
- ✅ Git history
- ✅ Local data in `/data/` directory
- ✅ Ability to redeploy anytime

### You **LOSE**:
- ❌ Cloud infrastructure (DynamoDB tables, Lambda functions, etc.)
- ❌ Any data stored only in DynamoDB (if not backed up)
- ❌ Live API Gateway endpoints
- ❌ OAuth tokens stored in Secrets Manager

### Cost **SAVED**:
- ✅ **$48/year** (~$4/month × 12 months)
- ✅ **Much more if Bedrock was used** ($500+/year possible!)

---

## 📝 Alternative: Minimal Cleanup

**If you want to keep Lambda code but reduce costs:**

### **Remove just the expensive parts:**

```bash
cd 01-personal/garmin-health/backend

# Edit terraform/api_gateway.tf
# Comment out all resources (saves $3.50/month)

# Edit terraform/secrets.tf
# Comment out resources (saves $0.40/month)

# Keep Lambda + DynamoDB (study/reference)

terraform apply
```

**Result**: ~$4/month → ~$0/month (free tier)

---

## 📞 Getting Help

### **Questions to ask before destroying:**
- "Will I need this in the next 6 months?" → If YES, keep
- "Is there important data in DynamoDB?" → If YES, back it up
- "Could Garmin API calls be happening automatically?" → Check logs!

### **If you're unsure:**
1. Run the audit script
2. Check CloudWatch logs
3. Review AWS Billing dashboard
4. Sleep on the decision
5. Then decide with confidence

---

## ✅ Final Checklist

Before running `terraform destroy`:

- [ ] Ran `bash scripts/audit-aws.sh` (confirmed infrastructure exists)
- [ ] Checked CloudWatch Logs (confirmed functions haven't run recently)
- [ ] Reviewed AWS Billing (confirmed no surprise charges)
- [ ] Backed up any important data (if needed)
- [ ] Ran `terraform plan -destroy` (reviewed what will be deleted)
- [ ] Decided this is the right action for your situation
- [ ] Understanding this **cannot be easily undone**

---

## 🎯 Recommended Decision

**For this student account:**

> **Recommendation: Run `terraform destroy` to remove all infrastructure**
>
> **Reasoning:**
> - Infrastructure is idle (~$4/month cost)
> - Code is safely stored in Git
> - Can redeploy anytime from Terraform
> - Protects against unexpected Bedrock charges
> - Aligns with student account best practices

**Cost savings**: **$48/year** (minimum)

---

## 📅 Post-Cleanup Tasks

After successful cleanup:

1. **Update TODO.md** to mark Garmin AWS cleanup as done
2. **Commit to Git**:
   ```bash
   git add AWS-AUDIT-REPORT.md AWS-CLEANUP-DECISION-GUIDE.md
   git commit -m "docs: add AWS audit and cleanup guides"
   git push
   ```
3. **Delete this decision guide** (or keep for future reference)
4. **Set up billing alerts** for any remaining AWS services:
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name "AWS-Monthly-Cost-Alert" \
     --alarm-description "Alert if monthly spend > $1" \
     --metric-name EstimatedCharges \
     --namespace AWS/Billing \
     --statistic Maximum \
     --period 86400 \
     --threshold 1 \
     --comparison-operator GreaterThanThreshold \
     --evaluation-periods 1
   ```

---

**Last Updated**: 2026-03-26
**Status**: Ready for your decision ✓
