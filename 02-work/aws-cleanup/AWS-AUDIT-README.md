# AWS Audit & Cleanup — START HERE

**Created**: 2026-03-26
**Status**: All resources mapped, ready for your decision
**Estimated Cost**: $3.93-$4.93/month (if deployed)

---

## 📌 Quick Summary

Based on my analysis of your codebase, here's what you have:

### ✅ What Exists (In Terraform Code)

| Component | Count | Status | Cost |
|-----------|-------|--------|------|
| **Lambda Functions** | 4 | Deployed? | $0-500+ (depends on usage) |
| **DynamoDB Tables** | 2 | Deployed? | $0 (on-demand, free tier) |
| **API Gateway** | 1 | Deployed? | $3.50/month |
| **Secrets Manager** | 1 | Deployed? | $0.40/month |
| **CloudWatch Logs** | 5 | Auto-created | $0.03/month |
| **EventBridge Rules** | 2 | Deployed? | $0 (free) |
| **SQS DLQ** | 1 | Deployed? | $0 (free) |

### 💰 Estimated Monthly Cost

**If infrastructure is deployed and idle**: **~$3.93/month**
**If Bedrock was actually used**: **$50-500+/month** ⚠️

---

## 🚀 Next Steps (Choose One)

### **Option A: Run Quick Audit (5 minutes) — RECOMMENDED FIRST**

```bash
cd 01-personal/garmin-health/backend
bash scripts/audit-aws.sh
```

This will:
- ✓ Verify if resources actually exist in AWS
- ✓ Show real costs (if any)
- ✓ List all Garmin infrastructure
- ✓ Check Bedrock usage (important!)

### **Option B: Review Decision Guide (10 minutes)**

Read: [`AWS-CLEANUP-DECISION-GUIDE.md`](./AWS-CLEANUP-DECISION-GUIDE.md)

This helps you decide: **Keep or destroy?**

### **Option C: Detailed Technical Audit (15 minutes)**

Read: [`AWS-AUDIT-REPORT.md`](./AWS-AUDIT-REPORT.md)

Complete technical breakdown with:
- All resource configurations
- Pricing details
- Cleanup procedures
- Verification commands

---

## ⚠️ Critical Issues to Check

### **1. Bedrock Invocations (Potential cost bomb)**

Your `ai_analyzer` Lambda can call Claude via Bedrock, which costs:
- **Input**: $3/million tokens
- **Output**: $15/million tokens

If this Lambda ran even 100 times with average prompts: **$100-500/month** 💸

**To check**: Run the audit script to see actual usage

### **2. API Gateway ($3.50/month base cost)**

Just having the API deployed costs $3.50/month, even if no one uses it.

**To check**: Run the audit script

### **3. DynamoDB Tables (Usually free, unless heavy use)**

Tables use on-demand billing (free tier: 25 WCU, 25 RCU/month)

**To check**: Run the audit script

---

## 🎯 Recommended Path

### **For Student Account (No Commercial Use)**

```
1. Run audit script (5 min)
   ↓
2. Check CloudWatch logs for Lambda invocations (2 min)
   ↓
3. Check AWS Billing dashboard for actual costs (2 min)
   ↓
4. If idle + costs < $1/month → DESTROY INFRASTRUCTURE
   ↓
5. Save code, redeploy anytime if needed later
```

**Expected outcome**: Save **$48/year** minimum

---

## 📂 Files Created for You

### **1. AWS-AUDIT-REPORT.md** (Technical Reference)
- Complete inventory of all resources
- Pricing breakdown by service
- Verification commands (copy-paste ready)
- Step-by-step cleanup procedures
- Billing alarm setup

### **2. AWS-CLEANUP-DECISION-GUIDE.md** (Decision Framework)
- Decision matrix (should you keep or destroy?)
- Safe destruction procedure
- Data backup instructions
- Post-cleanup verification
- Minimal cleanup alternative

### **3. scripts/audit-aws.sh** (Automation)
- Executable script to inspect your AWS account
- Safe, read-only (doesn't delete anything)
- Shows real deployed resources
- Lists costs and estimates
- Color-coded output

### **4. AWS-AUDIT-README.md** (This File)
- Quick overview
- How to proceed
- Critical things to check

---

## 🔐 Security Notes

**You should NEVER share AWS credentials with Claude or any AI.**

Instead:
1. ✅ I analyzed your **code** (Terraform configurations)
2. ✅ I provided **commands** you run with your own credentials
3. ✅ I provided **scripts** you execute locally
4. ❌ I did NOT access your AWS account
5. ❌ I did NOT see any actual deployed resources (you verify via script)

---

## 🛠️ Tool You'll Need

### **AWS CLI** (already mention in docs)

If you don't have it:
```bash
# Install AWS CLI
# https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

# Configure credentials (securely!)
aws configure
# This will ask for:
#   - Access Key ID
#   - Secret Access Key
#   - Default region (us-east-1)
```

---

## ❓ FAQ

### **Q: Will I lose my code if I destroy infrastructure?**
**A**: No! Your code is in Git. Only the cloud resources (Lambda, DynamoDB, etc.) are deleted. You can redeploy anytime.

### **Q: Can I undo terraform destroy?**
**A**: No, it's permanent. But since you have the code, you can recreate it.

### **Q: What about my DynamoDB data?**
**A**: Lost if not backed up first. The cleanup guide shows how to export before deleting.

### **Q: How much will Bedrock cost?**
**A**: Depends on usage. Check CloudWatch metrics with the audit script. Could be $0-500/month.

### **Q: What if I want to keep the code but remove infrastructure?**
**A**: That's fine! The code is in the repo. The infrastructure only exists if you run `terraform apply`.

### **Q: Is there a way to pause instead of delete?**
**A**: You can comment out resources in Terraform files, then `terraform apply`. Keeps code, removes resources.

---

## 📊 What the Audit Script Does

When you run `bash scripts/audit-aws.sh`, it will:

1. ✓ Check AWS CLI is installed
2. ✓ Verify your AWS credentials work
3. ✓ List all Lambda functions (Garmin-related)
4. ✓ List all DynamoDB tables (Garmin-related)
5. ✓ List all API Gateways (Garmin-related)
6. ✓ List all Secrets (Garmin-related)
7. ✓ List all CloudWatch log groups (Garmin-related)
8. ✓ List all EventBridge rules (Garmin-related)
9. ✓ List all IAM roles (Garmin-related)
10. ✓ Check for Bedrock agents/knowledge bases
11. ✓ Estimate monthly costs
12. ✓ Provide cleanup recommendations

**The script is read-only** — it doesn't change anything!

---

## 🚦 Decision Tree

```
Have you decided?
   ↓
NO → Read AWS-CLEANUP-DECISION-GUIDE.md → Run audit script
   ↓
YES, KEEP → Set billing alerts, monitor monthly
   ↓
YES, DESTROY → Follow cleanup procedure in AWS-AUDIT-REPORT.md
   ↓
DONE → Verify with audit script
```

---

## ✅ Confidence Level

After following these guides:
- ✅ You'll know **exactly** what's deployed
- ✅ You'll know **exactly** what it costs
- ✅ You'll have a **safe** cleanup procedure
- ✅ You can make an **informed** decision
- ✅ You can **execute** without surprises

---

## 📞 Need Help?

### **Before destroying:**
1. Run `bash scripts/audit-aws.sh`
2. Compare against AWS console (Billing → Cost Explorer)
3. Check CloudWatch logs for evidence of usage
4. Read the decision guide

### **If something goes wrong:**
- Nothing has been deleted yet (scripts are read-only)
- All destructive commands require explicit `terraform destroy`
- Terraform will ask for confirmation before deleting

---

## 🎯 Recommended First Action

**Right now, run this:**

```bash
cd 01-personal/garmin-health/backend
bash scripts/audit-aws.sh
```

This takes 30 seconds and will tell you exactly what you have.

Then decide based on the output!

---

**Files to read in order:**
1. ← You are here (AWS-AUDIT-README.md)
2. Run the audit script
3. Read AWS-CLEANUP-DECISION-GUIDE.md
4. Optionally: Read AWS-AUDIT-REPORT.md for details

---

**Status**: ✅ Ready for your decision
**Last Updated**: 2026-03-26
**Created by**: Claude Code Security Audit
