# Garmin Health — Quickstart Guide

Get the analytics dashboard running in ~20 minutes, or deploy the full backend in ~45 minutes.

---

## Quick Option: Dashboard Only (15 min)

See your Garmin health data visualized locally with AI insights. No AWS setup needed.

### Prerequisites
- Python 3.11+
- Garmin data exports (JSON files)
- Anthropic API key

### Steps

```bash
# 1. Navigate to analytics
cd 01-personal/garmin-health/analytics

# 2. Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add:
# ANTHROPIC_API_KEY=sk-ant-...

# 5. Link data files
# Copy your Garmin JSON exports to ../data/raw/
mkdir -p ../data/raw
cp /path/to/nesihaver@gmail.com_0_summarizedActivities.json ../data/raw/
cp /path/to/sleep_all_merged.json ../data/raw/
cp /path/to/wellness_all_merged.json ../data/raw/

# 6. Run the dashboard
streamlit run app.py
```

✅ **Open your browser** to `http://localhost:8501`

**What you'll see:**
- Running activity trends
- Sleep analysis with AI coaching
- Training load recommendations
- Personalized health insights from Claude AI

---

## Full Option: AWS Backend + Dashboard (45 min)

Deploy the complete pipeline: Garmin API webhook → Lambda → DynamoDB → Streamlit.

### Prerequisites
- AWS account
- Terraform
- AWS CLI configured
- Garmin API access

### Steps

#### Phase 1: Dashboard (15 min, same as above)
Follow "Quick Option" steps 1-6 above.

#### Phase 2: AWS Backend Deployment (30 min)

```bash
# 1. Navigate to backend
cd 01-personal/garmin-health/backend

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure AWS
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Region (us-east-1), Output (json)

# 4. Setup environment variables
cp config/.env.example config/.env
cp config/terraform.tfvars.example config/terraform.tfvars

# Edit config/.env with your Garmin API credentials:
# GARMIN_CLIENT_ID=...
# GARMIN_CLIENT_SECRET=...
# GARMIN_USERNAME=...
# GARMIN_PASSWORD=...

# Edit config/terraform.tfvars:
# aws_region = "us-east-1"
# environment = "development"

# 5. Deploy infrastructure
cd terraform
terraform init

# Review what will be created
terraform plan -var-file="../config/terraform.tfvars"

# Deploy (takes ~5-10 minutes)
terraform apply -var-file="../config/terraform.tfvars"

# 6. Note the outputs
# Copy the API Gateway endpoint URL

# 7. Test the deployment
cd ..
bash scripts/test_oauth_flow.sh

# 8. Get Garmin webhook URL from CloudFormation outputs
# Register webhook in Garmin API dashboard
```

✅ **Backend is live**. Garmin data will auto-sync to DynamoDB whenever your device uploads new activities.

---

## What's Running Now?

```
Garmin Device
    ↓ (webhook on new activity)
API Gateway (AWS)
    ↓
Lambda Function (fetch_activity)
    ↓
DynamoDB Table (activities)
    ↓
Streamlit Dashboard (queries DynamoDB + calls Claude AI)
    ↓
Your Browser
```

---

## Next Steps

### Load Historical Data
```bash
cd backend
bash scripts/backfill_activities.sh
# Fetches all historical Garmin data and populates DynamoDB
```

### View Logs
```bash
# CloudWatch logs
aws logs tail /aws/lambda/garmin-fetch-activity --follow

# Local dashboard logs
# Streamlit logs appear in terminal where you ran `streamlit run app.py`
```

### Customize Dashboard
Edit `analytics/src/` modules:
- `ai_insights.py` — Change Claude AI prompts
- `charts.py` — Modify visualizations
- `metrics.py` — Add new health metrics
- `data_loader.py` — Change data queries

### Manage Costs
```bash
# View Lambda invocation counts
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=garmin-fetch-activity \
  --start-time 2026-04-01T00:00:00Z \
  --end-time 2026-04-13T00:00:00Z \
  --period 86400 \
  --statistics Sum
```

---

## Troubleshooting

### "Streamlit: command not found"
```bash
# Activate venv first
cd analytics
source .venv/bin/activate
streamlit run app.py
```

### "ModuleNotFoundError: anthropic"
```bash
pip install -r requirements.txt
```

### "PermissionError" when creating data directories
```bash
mkdir -p data/{raw,processed,exports}
chmod 755 data/
```

### Lambda function not receiving webhooks
1. Verify webhook URL in Garmin API dashboard matches CloudFormation output
2. Check DynamoDB table exists: `aws dynamodb list-tables`
3. View Lambda logs: `aws logs tail /aws/lambda/garmin-fetch-activity --follow`

### DynamoDB table not found
```bash
# Verify table was created
aws dynamodb describe-table --table-name garmin_activities

# If missing, re-run terraform apply
cd terraform
terraform apply -var-file="../config/terraform.tfvars"
```

### Data not appearing in dashboard
1. Check data files in `data/raw/` exist
2. Verify file format is valid JSON: `python -m json.tool data/raw/activities.json`
3. Check DynamoDB table has items: `aws dynamodb scan --table-name garmin_activities`

---

## Common Commands

```bash
# Dashboard only
cd analytics && streamlit run app.py

# Backend: Check infrastructure status
cd backend/terraform && terraform show

# Backend: View recent Lambda invocations
aws lambda list-function-event-invoke-configs --function-name garmin-fetch-activity

# Backend: Clear all data (careful!)
aws dynamodb scan --table-name garmin_activities --projection-expression "id" | \
  jq '.Items[].id.S' | \
  xargs -I {} aws dynamodb delete-item --table-name garmin_activities --key "{\"id\": {\"S\": \"{}\"}, \"date\": {\"S\": \"2026-01-01\"}}"

# Run tests
cd backend && python -m pytest tests/ -v

# Deploy infrastructure
cd backend/terraform && terraform apply -var-file="../config/terraform.tfvars"

# Destroy infrastructure (careful!)
cd backend/terraform && terraform destroy -var-file="../config/terraform.tfvars"
```

---

## Full Documentation

- **Development**: [CLAUDE.md](CLAUDE.md)
- **Architecture**: [README.md](README.md)
- **Decisions**: [DECISIONS.md](DECISIONS.md)
- **Active work**: [TODO.md](TODO.md)
- **API reference**: See AWS Lambda function comments in `backend/lambda/`

---

**Last updated**: 2026-04-13  
**Tested on**: Python 3.11, macOS 14, Ubuntu 22.04
