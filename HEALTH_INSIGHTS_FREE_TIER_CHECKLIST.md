# Health Insights Agent - Free Tier Implementation Checklist

**Target Cost:** $0.42-5/month
**Purpose:** Personal learning project
**Timeline:** 7-9 days

---

## Phase 0: Setup & Prerequisites ☁️

**Goal:** Prepare AWS account and development environment

### AWS Account Configuration
- [ ] Create AWS account (or use existing)
- [ ] Enable free tier tracking in Billing Console
- [ ] Set up billing alerts:
  - [ ] Alert at $5
  - [ ] Alert at $10
  - [ ] Alert at $20
- [ ] Enable Cost Explorer
- [ ] Create free tier budget (first 2 budgets are free)

### Bedrock Model Access
- [ ] Go to AWS Console → Bedrock → Model access
- [ ] Request access to **Claude 3 Haiku** (cheapest option!)
- [ ] Request access to **Titan Embeddings G1 - Text**
- [ ] Wait for approval (usually instant)
- [ ] Verify access granted

### Development Tools
- [ ] Install AWS CLI: `pip install awscli`
- [ ] Configure AWS CLI: `aws configure`
- [ ] Install Python dependencies: `pip install boto3 garminconnect`
- [ ] Test AWS access: `aws sts get-caller-identity`

### Cost Monitoring
- [ ] Set up AWS Budgets
- [ ] Subscribe to AWS Free Tier usage alerts
- [ ] Bookmark AWS Cost Explorer

**Time:** 1-2 hours

---

## Phase 1: Garmin Data Pipeline 🏊🏃

**Goal:** Automatically sync health data from Garmin Connect to AWS

### 1.1 Create DynamoDB Tables

- [ ] Create **HealthInsights-Activities** table
  ```bash
  aws dynamodb create-table \
    --table-name HealthInsights-Activities \
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=timestamp,AttributeType=S \
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
  ```

- [ ] Create **HealthInsights-SleepData** table
  ```bash
  aws dynamodb create-table \
    --table-name HealthInsights-SleepData \
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=date,AttributeType=S \
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=date,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
  ```

- [ ] Create **HealthInsights-UserMemory** table
  ```bash
  aws dynamodb create-table \
    --table-name HealthInsights-UserMemory \
    --attribute-definitions AttributeName=userId,AttributeType=S AttributeName=memoryKey,AttributeType=S \
    --key-schema AttributeName=userId,KeyType=HASH AttributeName=memoryKey,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST
  ```

- [ ] Verify tables created: `aws dynamodb list-tables`

### 1.2 Store Garmin Credentials

- [ ] Store credentials in Secrets Manager
  ```bash
  aws secretsmanager create-secret \
    --name health-insights/garmin \
    --secret-string '{"email":"your@email.com","password":"yourpassword"}'
  ```
- [ ] Test retrieval: `aws secretsmanager get-secret-value --secret-id health-insights/garmin`

**Cost:** $0.40/month (unavoidable for Secrets Manager)

### 1.3 Create IAM Role for Lambda

- [ ] Create `trust-policy.json`:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }
  ```

- [ ] Create IAM role:
  ```bash
  aws iam create-role \
    --role-name HealthInsightsLambdaRole \
    --assume-role-policy-document file://trust-policy.json
  ```

- [ ] Attach policies:
  ```bash
  aws iam attach-role-policy \
    --role-name HealthInsightsLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

  aws iam attach-role-policy \
    --role-name HealthInsightsLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

  aws iam attach-role-policy \
    --role-name HealthInsightsLambdaRole \
    --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
  ```

### 1.4 Create GarminDataFetcher Lambda

- [ ] Create directory: `mkdir -p lambda/garmin_fetcher`
- [ ] Create `lambda/garmin_fetcher/lambda_function.py` (see plan document)
- [ ] Install dependencies:
  ```bash
  cd lambda/garmin_fetcher
  pip install garminconnect -t .
  ```
- [ ] Create deployment package:
  ```bash
  zip -r function.zip .
  ```
- [ ] Deploy Lambda:
  ```bash
  aws lambda create-function \
    --function-name GarminDataFetcher \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/HealthInsightsLambdaRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 60 \
    --memory-size 256
  ```

### 1.5 Test Lambda Manually

- [ ] Invoke Lambda:
  ```bash
  aws lambda invoke \
    --function-name GarminDataFetcher \
    --payload '{}' \
    response.json
  ```
- [ ] Check response: `cat response.json`
- [ ] Verify data in DynamoDB:
  ```bash
  aws dynamodb scan --table-name HealthInsights-Activities --limit 5
  aws dynamodb scan --table-name HealthInsights-SleepData --limit 5
  ```
- [ ] Check CloudWatch logs:
  ```bash
  aws logs tail /aws/lambda/GarminDataFetcher --follow
  ```

### 1.6 Schedule with EventBridge

- [ ] Create EventBridge rule:
  ```bash
  aws events put-rule \
    --name GarminHourlySync \
    --schedule-expression "rate(1 hour)"
  ```

- [ ] Add Lambda as target:
  ```bash
  aws events put-targets \
    --rule GarminHourlySync \
    --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT_ID:function:GarminDataFetcher"
  ```

- [ ] Grant permission:
  ```bash
  aws lambda add-permission \
    --function-name GarminDataFetcher \
    --statement-id EventBridgeInvoke \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com
  ```

- [ ] Wait 1 hour and verify automatic sync works

**Success Criteria:**
- ✅ Lambda fetches Garmin data successfully
- ✅ Data appears in DynamoDB
- ✅ EventBridge triggers every hour
- ✅ Cost: $0 (within free tier)

**Time:** 3-4 hours

---

## Phase 2: Bedrock Agent with Actions 🤖

**Goal:** Create AI agent that can query your health data

### 2.1 Create Action Handler Lambda

- [ ] Create directory: `mkdir -p lambda/action_handler`
- [ ] Create `lambda/action_handler/lambda_function.py` (see plan document)
- [ ] Create deployment package:
  ```bash
  cd lambda/action_handler
  zip -r function.zip lambda_function.py
  ```
- [ ] Deploy Lambda:
  ```bash
  aws lambda create-function \
    --function-name HealthInsightsActionHandler \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/HealthInsightsLambdaRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --timeout 30 \
    --memory-size 256
  ```

### 2.2 Create OpenAPI Schema

- [ ] Create directory: `mkdir -p bedrock`
- [ ] Create `bedrock/action_group_schema.json` (see plan document)
- [ ] Validate JSON: `python -m json.tool action_group_schema.json`

### 2.3 Create Bedrock Agent (AWS Console)

- [ ] Go to AWS Console → Bedrock → Agents → Create Agent
- [ ] **Agent Details:**
  - [ ] Name: `HealthInsightsCoach`
  - [ ] Description: `Personal health coaching agent`
  - [ ] Enable user input

- [ ] **Agent Instructions:** (Choose Option A or B)

**Option A: In-Memory Knowledge (FREE - Recommended)**
- [ ] Use agent instructions that include embedded coaching knowledge (see plan document)
- [ ] Cost: $0

**Option B: With Knowledge Base (~$60/month)**
- [ ] Use basic agent instructions
- [ ] Skip KB for now, add later if desired

- [ ] **Model Selection:**
  - [ ] Model: **Claude 3 Haiku** (12x cheaper!)
  - [ ] Temperature: 1.0
  - [ ] Top P: 0.999

- [ ] **Add Action Group:**
  - [ ] Name: `HealthDataTools`
  - [ ] Description: `Retrieve activity, sleep, and memory data`
  - [ ] Type: Define with API schemas
  - [ ] Upload `action_group_schema.json`
  - [ ] Executor: Lambda → `HealthInsightsActionHandler`

- [ ] **Create Agent**

- [ ] **Create Alias:**
  - [ ] Name: `prod`
  - [ ] Description: `Production alias`

### 2.4 Grant Permissions

- [ ] Grant Bedrock permission to invoke Lambda:
  ```bash
  aws lambda add-permission \
    --function-name HealthInsightsActionHandler \
    --statement-id AllowBedrockInvoke \
    --action lambda:InvokeFunction \
    --principal bedrock.amazonaws.com \
    --source-arn arn:aws:bedrock:REGION:ACCOUNT_ID:agent/AGENT_ID
  ```

### 2.5 Test Agent in Console

- [ ] Click "Test" button in Bedrock console
- [ ] Try: "What were my swimming sessions this week?"
- [ ] Try: "How is my sleep quality?"
- [ ] Try: "Show me my running data"
- [ ] Verify agent retrieves real data from DynamoDB
- [ ] Check responses are helpful and personalized

**Success Criteria:**
- ✅ Agent created successfully
- ✅ Agent invokes action group Lambda
- ✅ Agent returns real data
- ✅ Responses are coaching-style (not just data dumps)
- ✅ Cost: $0-2 for testing

**Time:** 2-3 hours

---

## Phase 3: Knowledge Integration (Optional) 📚

**Goal:** Add coaching expertise

### Option A: In-Memory Knowledge (FREE) ✅ Recommended

- [x] Already included in agent instructions from Phase 2
- [ ] Test technique questions:
  - [ ] "What is a good SWOLF score?"
  - [ ] "How should I train for a half marathon?"
  - [ ] "What affects sleep quality?"

**Cost:** $0
**Time:** 0 hours (already done!)

### Option B: Bedrock Knowledge Base (~$60/month)

**Only do this if you want to learn vector search RAG**

- [ ] Create S3 bucket:
  ```bash
  aws s3 mb s3://health-insights-kb-YOUR-ACCOUNT-ID
  ```

- [ ] Create coaching documents:
  - [ ] `swimming-technique.md`
  - [ ] `running-training.md`
  - [ ] `sleep-recovery.md`

- [ ] Upload to S3:
  ```bash
  aws s3 cp swimming-technique.md s3://health-insights-kb-YOUR-ACCOUNT-ID/
  aws s3 cp running-training.md s3://health-insights-kb-YOUR-ACCOUNT-ID/
  aws s3 cp sleep-recovery.md s3://health-insights-kb-YOUR-ACCOUNT-ID/
  ```

- [ ] Create Knowledge Base in AWS Console:
  - [ ] Name: `HealthCoachingKB`
  - [ ] Data source: S3
  - [ ] Embedding model: Titan Embeddings G1
  - [ ] Vector database: OpenSearch Serverless (required, expensive!)

- [ ] Sync data source

- [ ] Associate KB with agent

- [ ] Test combined queries

**Cost:** ~$60/month
**Time:** 2 hours

**Recommendation:** Skip for now, use Option A

---

## Phase 4: CLI Interface 💻

**Goal:** Chat with your agent from command line

### 4.1 Create Chat Script

- [ ] Create `chat.py` in project root (see plan document)
- [ ] Make executable: `chmod +x chat.py`
- [ ] Update `AGENT_ID` in script (from Bedrock console)
- [ ] Update `AGENT_ALIAS_ID` in script (from Bedrock console)

### 4.2 Test Chat Interface

- [ ] Run: `./chat.py`
- [ ] Try conversation:
  ```
  You: What were my swimming sessions this week?
  [Wait for response]

  You: How is my sleep?
  [Wait for response]

  You: What should I focus on to improve?
  [Wait for response]

  You: quit
  ```

- [ ] Verify:
  - [ ] Agent retrieves real data
  - [ ] Responses are personalized
  - [ ] Multi-turn conversation works
  - [ ] Session context maintained

**Success Criteria:**
- ✅ CLI interface works smoothly
- ✅ Agent responses are helpful
- ✅ Conversation feels natural
- ✅ Cost: $0 (uses existing agent)

**Time:** 30 minutes

---

## Phase 5: Memory & Goals 🧠

**Goal:** Teach agent to remember your goals

### 5.1 Set Goals

- [ ] Run `./chat.py`
- [ ] Set swimming goal:
  ```
  You: I want to improve my 100m freestyle time to under 1:30
  [Agent should acknowledge and save goal]
  ```

- [ ] Set running goal:
  ```
  You: My goal is to complete a half marathon in under 1:45
  [Agent should acknowledge and save goal]
  ```

- [ ] Set sleep goal:
  ```
  You: I want to get 8 hours of sleep at least 5 nights per week
  [Agent should acknowledge and save goal]
  ```

- [ ] Quit: `quit`

### 5.2 Verify Memory Persistence

- [ ] Check DynamoDB:
  ```bash
  aws dynamodb scan --table-name HealthInsights-UserMemory
  ```
- [ ] Verify goals are stored

### 5.3 Test Goal Recall

- [ ] Start new chat session: `./chat.py`
- [ ] Ask: "What are my swimming goals?"
  - [ ] Agent should recall: 100m freestyle under 1:30
- [ ] Ask: "What are my running goals?"
  - [ ] Agent should recall: half marathon under 1:45
- [ ] Ask: "Give me advice based on my goals"
  - [ ] Agent should reference goals in advice

### 5.4 Test Coaching Insights

- [ ] Have conversation about recent training
- [ ] Agent should mention goals when relevant
- [ ] Agent should save insights to memory
- [ ] Exit and restart
- [ ] Agent should reference previous insights

**Success Criteria:**
- ✅ Goals persist across sessions
- ✅ Agent references goals in advice
- ✅ Agent saves and recalls insights
- ✅ Coaching feels continuous
- ✅ Cost: $0 (within free tier)

**Time:** 1 hour

---

## Final Testing & Validation ✅

### Cost Verification

- [ ] Go to AWS Cost Explorer
- [ ] Check current month costs
- [ ] Verify breakdown:
  - [ ] Bedrock Haiku: $0-5
  - [ ] Lambda: $0 (free tier)
  - [ ] DynamoDB: $0 (free tier)
  - [ ] Secrets Manager: $0.40
  - [ ] Other: $0
- [ ] **Total should be under $5/month**

### Free Tier Monitoring

- [ ] Check free tier usage:
  - [ ] DynamoDB: Should be well under 25 RCU/WCU
  - [ ] Lambda: Should be under 1M requests
  - [ ] S3: Should be under 5GB
- [ ] Set up alerts if approaching limits

### End-to-End Test

- [ ] **Scenario 1: Data Check**
  ```
  You: What activities did I do this week?
  Expected: Lists swimming and running sessions with metrics
  ```

- [ ] **Scenario 2: Sleep Analysis**
  ```
  You: How is my sleep this week?
  Expected: Sleep summary with averages and insights
  ```

- [ ] **Scenario 3: Coaching Advice**
  ```
  You: I swam 2000m today with SWOLF of 45. How can I improve?
  Expected: Specific technique advice referencing SWOLF knowledge
  ```

- [ ] **Scenario 4: Goal Tracking**
  ```
  You: How am I progressing toward my 100m freestyle goal?
  Expected: Compares current pace to goal, gives actionable plan
  ```

- [ ] **Scenario 5: Cross-domain Advice**
  ```
  You: My running felt hard today and I slept poorly last night. What should I do?
  Expected: Correlates sleep and training, recommends recovery
  ```

### Documentation

- [ ] Document your agent ID and alias ID
- [ ] Note any customizations you made
- [ ] Document any issues encountered
- [ ] Write down cost-saving tips you discovered

---

## Post-Implementation: Next Steps 🚀

### Learning Extensions

- [ ] **Add Simple Web UI**
  - [ ] Create HTML/JS chat interface
  - [ ] Deploy to S3 static hosting (free)
  - [ ] Use API Gateway (free tier)

- [ ] **Add Knowledge Base**
  - [ ] Compare in-memory vs vector search
  - [ ] Learn about embeddings
  - [ ] Understand RAG trade-offs

- [ ] **Add Advanced Features**
  - [ ] Training plan generation
  - [ ] Weekly summary emails (SES free tier)
  - [ ] Progress charts

- [ ] **Try Other Frameworks**
  - [ ] Build same agent with LangChain
  - [ ] Try AWS AgentCore
  - [ ] Compare approaches

### Cost Optimization

- [ ] Review actual costs after 1 month
- [ ] Identify any unexpected charges
- [ ] Optimize token usage if needed
- [ ] Consider caching frequent queries

### Share & Learn

- [ ] Write blog post about what you learned
- [ ] Share on GitHub
- [ ] Help others build similar agents
- [ ] Join AI agent communities

---

## Troubleshooting 🔧

### Common Issues

**Lambda can't access DynamoDB:**
- [ ] Check IAM role has DynamoDB permissions
- [ ] Verify table names are correct
- [ ] Check region matches

**Garmin authentication fails:**
- [ ] Verify credentials in Secrets Manager
- [ ] Test Garmin login in browser
- [ ] Check garminconnect library is up to date

**Agent doesn't call tools:**
- [ ] Check Lambda permissions in Bedrock
- [ ] Verify OpenAPI schema is valid
- [ ] Test Lambda function directly
- [ ] Check CloudWatch logs

**Costs higher than expected:**
- [ ] Check Bedrock token usage
- [ ] Verify using Haiku not Sonnet
- [ ] Look for unexpected Lambda invocations
- [ ] Check for runaway EventBridge rules

**Chat script fails:**
- [ ] Verify AWS credentials configured
- [ ] Check agent ID and alias ID are correct
- [ ] Ensure boto3 is installed
- [ ] Check region is correct

---

## Summary 📊

### What You Built

- ✅ Automated Garmin data pipeline
- ✅ Bedrock Agent with Claude Haiku
- ✅ Action groups for data retrieval
- ✅ Memory system for goals and insights
- ✅ CLI chat interface
- ✅ Hourly automated sync

### What You Learned

- ✅ AI agent architecture and orchestration
- ✅ AWS Bedrock Agents setup and configuration
- ✅ Lambda functions and triggers
- ✅ DynamoDB data modeling
- ✅ EventBridge scheduling
- ✅ IAM permissions and security
- ✅ Cost optimization strategies
- ✅ RAG concepts (in-memory vs vector DB)

### Cost Achievement

**Target:** $0-5/month
**Actual:** $_________ (fill in after 1 month)

**Comparison to original plan:**
- Original: ~$95/month
- Optimized: ~$0.42/month
- **Savings: ~99.5%!** 🎉

### Time Investment

**Estimated:** 7-9 days (2-3 hours/day)
**Actual:** _________ (fill in your actual time)

---

**Congratulations!** 🎉

You've built a production-quality AI agent while staying within AWS free tier. You now understand how AI agents work and can build more complex systems in the future!

**Last Updated:** 2026-01-16
**Status:** Ready to start!
