# Garmin Connect API Integration - Quick Reference

**Last Updated:** 2026-01-17
**Status:** Ready to use

---

## 🚀 Quick Start (5 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./garmin_quickstart.sh

# Edit credentials
nano .env

# Test connection
source venv/bin/activate
python test_garmin.py
```

### Option 2: Manual Setup

```bash
# Install dependencies
pip install garminconnect boto3 python-dotenv

# Set environment variables
export GARMIN_EMAIL="your@email.com"
export GARMIN_PASSWORD="yourpassword"

# Run example
python garmin_integration_example.py
```

---

## 📁 Files Created

| File | Purpose | When to Use |
|------|---------|-------------|
| `garmin_integration_example.py` | Full working code with AWS Lambda integration | Development & Production |
| `garmin_health_api_guide.md` | Complete guide for all 3 integration options | Reference & Planning |
| `garmin_quickstart.sh` | Automated setup script | Initial setup |
| `test_garmin.py` | Quick connection tester | Testing credentials |
| `.env` | Credentials storage (created by quickstart.sh) | Local development |

---

## 🔄 Integration Options

### 1️⃣ Unofficial Python Library (RECOMMENDED FOR YOU)

**Best for:** Personal projects, POC, learning, your Health Insights Agent

**Pros:**
- ✅ Works in 5 minutes
- ✅ Free forever
- ✅ Full access to YOUR data
- ✅ Perfect for AWS Lambda

**Cons:**
- ❌ Not for commercial apps
- ❌ Could break if Garmin changes website

**Setup:**
```bash
./garmin_quickstart.sh
```

**Code Example:**
```python
from garminconnect import Garmin

client = Garmin("email@example.com", "password")
client.login()

# Get swimming activities
activities = client.get_activities(0, 50)
swimming = [a for a in activities
            if 'swimming' in a['activityType']['typeKey']]

# Get sleep data
sleep = client.get_sleep_data('2026-01-17')
```

---

### 2️⃣ Official Garmin Health API

**Best for:** Commercial apps, production systems, multi-user platforms

**Pros:**
- ✅ Official support
- ✅ OAuth 2.0
- ✅ Webhooks
- ✅ SLA guarantees

**Cons:**
- ❌ 2-8 weeks approval
- ❌ Enterprise pricing
- ❌ Complex OAuth flow

**When to migrate:**
- When you're ready to launch to other users
- When you need commercial license
- When you have funding/budget

**Cost:** $500-2,000/month (estimated)

**Application:** https://developer.garmin.com/health-api/

---

### 3️⃣ Manual Export

**Best for:** One-time analysis, backups, historical data

**Process:**
1. Login to https://connect.garmin.com
2. Export activities as FIT/TCX files
3. Parse with `fitparse` library
4. Upload to S3

**Code:**
```bash
pip install fitparse

python << EOF
from fitparse import FitFile
fitfile = FitFile('activity.fit')
for record in fitfile.get_messages('record'):
    print(record)
EOF
```

---

## 🎯 Recommendation for Your Health Insights Agent

Based on your `HEALTH_INSIGHTS_AGENT_PLAN.md`:

### Phase 1: Use Unofficial Library (Now - 8 weeks)

```
Week 1-2: Foundation
├─ ✅ Run: ./garmin_quickstart.sh
├─ ✅ Test: python test_garmin.py
├─ ✅ Implement: Lambda GarminDataFetcher
└─ ✅ Store: Data in DynamoDB

Week 3-4: Integration with Bedrock Agent
├─ Use garmin_integration_example.py as template
├─ Deploy Lambda with EventBridge trigger
└─ Test agent with real Garmin data

Week 5-8: Refine and Test
├─ Add error handling
├─ Implement retry logic
└─ Test with various activity types
```

### Phase 2: Apply for Official API (Week 8+)

While using unofficial library, submit application for official API:

```
Week 8: Submit Application
├─ Apply at developer.garmin.com
├─ Prepare privacy policy
└─ Document use case

Week 10-16: Wait for Approval
├─ Continue development with unofficial library
├─ Design OAuth flow
└─ Plan migration strategy

Week 16+: Migrate to Official API
├─ Implement OAuth
├─ Update Lambda functions
└─ Enable for other users
```

---

## 💻 AWS Lambda Integration

### Deploy GarminDataFetcher Lambda

```bash
# 1. Create deployment package
cd lambda
pip install garminconnect -t .
zip -r function.zip .

# 2. Create Lambda function
aws lambda create-function \
    --function-name GarminDataFetcher \
    --runtime python3.11 \
    --role arn:aws:iam::ACCOUNT:role/LambdaGarminRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 60 \
    --memory-size 512

# 3. Store credentials in Secrets Manager
aws secretsmanager create-secret \
    --name garmin-credentials \
    --secret-string '{"email":"your@email.com","password":"password"}'

# 4. Create EventBridge rule (hourly sync)
aws events put-rule \
    --name GarminHourlySync \
    --schedule-expression "rate(1 hour)"

aws events put-targets \
    --rule GarminHourlySync \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:GarminDataFetcher"
```

### Lambda Code

Use `garmin_integration_example.py` - the `lambda_handler()` function is ready to deploy!

---

## 🔐 Security Best Practices

### ✅ DO:

- ✅ Store credentials in AWS Secrets Manager
- ✅ Use environment variables locally
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate passwords every 90 days
- ✅ Use encryption at rest (DynamoDB, S3)
- ✅ Enable CloudWatch logging

### ❌ DON'T:

- ❌ Commit credentials to git
- ❌ Hardcode passwords in code
- ❌ Share credentials with others
- ❌ Use unofficial library for commercial apps
- ❌ Store passwords in plain text
- ❌ Disable 2FA on Garmin account

### Secrets Manager Setup

```python
import boto3
import json

# Store credentials
client = boto3.client('secretsmanager')
client.create_secret(
    Name='garmin-credentials',
    Description='Garmin Connect login credentials',
    SecretString=json.dumps({
        'email': 'your@email.com',
        'password': 'yourpassword'
    })
)

# Retrieve in Lambda
def get_garmin_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='garmin-credentials')
    return json.loads(response['SecretString'])
```

---

## 🐛 Troubleshooting

### Authentication Fails

**Problem:** `GarminConnectAuthenticationError`

**Solutions:**
1. Check email/password are correct
2. Try logging in at https://connect.garmin.com first
3. Disable 2FA or use app-specific password
4. Check for account suspension (too many requests)

### No Data Returned

**Problem:** Activities/sleep data is empty

**Solutions:**
1. Verify you have activities in Garmin Connect
2. Check date range parameters
3. Ensure device has synced recently
4. Try fetching different data types

### Lambda Timeout

**Problem:** Lambda times out after 3 seconds

**Solutions:**
1. Increase timeout to 60 seconds
2. Reduce number of activities fetched
3. Use pagination for large datasets
4. Consider async processing

### Rate Limiting

**Problem:** Requests blocked after many calls

**Solutions:**
1. Add delays between requests (`time.sleep(1)`)
2. Reduce sync frequency (e.g., every 6 hours instead of hourly)
3. Cache data locally
4. Consider official API for production

---

## 📊 Data Structure Reference

### Activities Schema

```json
{
  "activityId": 12345678,
  "activityName": "Morning Run",
  "activityType": {
    "typeKey": "running",
    "typeId": 1
  },
  "startTimeLocal": "2026-01-17T07:30:00",
  "duration": 2400,
  "distance": 5000,
  "averageSpeed": 2.08,
  "averageHR": 155,
  "maxHR": 175,
  "calories": 350
}
```

### Sleep Data Schema

```json
{
  "sleepTimeSeconds": 28800,
  "deepSleepSeconds": 7200,
  "lightSleepSeconds": 18000,
  "remSleepSeconds": 3600,
  "awakeSleepSeconds": 1200,
  "sleepScores": {
    "overall": {"value": 85},
    "quality": {"value": 80},
    "duration": {"value": 90}
  }
}
```

---

## 📈 Next Steps

### Immediate (Today)

1. ✅ Run `./garmin_quickstart.sh`
2. ✅ Test with `python test_garmin.py`
3. ✅ Review `garmin_integration_example.py`

### Short-term (This Week)

1. 📝 Implement Lambda function for data fetching
2. 📝 Set up DynamoDB tables
3. 📝 Create EventBridge trigger
4. 📝 Test end-to-end pipeline

### Medium-term (This Month)

1. 🎯 Integrate with Bedrock Agent
2. 🎯 Add action groups for data retrieval
3. 🎯 Test agent with real Garmin data
4. 🎯 Implement error handling and retries

### Long-term (Next Quarter)

1. 🚀 Apply for official Garmin Health API
2. 🚀 Plan OAuth migration
3. 🚀 Add multi-user support
4. 🚀 Launch to beta users

---

## 📚 Additional Resources

### Documentation

- **Your Files:**
  - `HEALTH_INSIGHTS_AGENT_PLAN.md` - Full implementation plan
  - `HEALTH_INSIGHTS_CHECKLIST.md` - Step-by-step checklist
  - `AWS_BEDROCK_AGENT_PLAN.md` - Bedrock agent guide

- **External:**
  - [garminconnect Library](https://github.com/cyberjunky/python-garminconnect)
  - [Official Garmin API](https://developer.garmin.com/health-api/)
  - [AWS Lambda Guide](https://docs.aws.amazon.com/lambda/)
  - [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)

### Support

- **Library Issues:** https://github.com/cyberjunky/python-garminconnect/issues
- **Official API:** developer.garmin.com/support
- **AWS Support:** AWS Support Console

---

## ✅ Checklist

- [ ] Run quickstart script
- [ ] Add Garmin credentials to .env
- [ ] Test connection with test_garmin.py
- [ ] Review garmin_integration_example.py
- [ ] Store credentials in AWS Secrets Manager
- [ ] Create Lambda function
- [ ] Set up EventBridge trigger
- [ ] Test Lambda with sample data
- [ ] Create DynamoDB tables
- [ ] Test end-to-end pipeline
- [ ] Integrate with Bedrock Agent
- [ ] Consider applying for official API

---

**Questions?** Check the troubleshooting section or review the detailed guide in `garmin_health_api_guide.md`

**Ready to start?** Run: `./garmin_quickstart.sh`

Good luck! 🚀
