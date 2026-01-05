# Personal Finance & Health Analysis Agent
## AWS Bedrock Agent Implementation Plan

## Overview
This document provides a customized implementation plan for building an AI agent that can:
- Analyze personal financial documents (mortgage, contracts, statements)
- Provide financial insights and decision support
- Track and analyze Garmin health activity data
- Answer questions about your health trends and fitness goals
- Make personalized recommendations based on your data

**⚠️ IMPORTANT: This agent will handle sensitive personal and health information. Security and privacy are paramount.**

---

## Table of Contents
1. [Use Case Definition](#use-case-definition)
2. [Architecture Overview](#architecture-overview)
3. [Security & Privacy First](#security--privacy-first)
4. [Phase 1: AWS Security Setup](#phase-1-aws-security-setup)
5. [Phase 2: Document Knowledge Base](#phase-2-document-knowledge-base)
6. [Phase 3: Garmin Health Integration](#phase-3-garmin-health-integration)
7. [Phase 4: Agent Configuration](#phase-4-agent-configuration)
8. [Phase 5: Testing & Validation](#phase-5-testing--validation)
9. [Phase 6: Deployment](#phase-6-deployment)
10. [Example Queries](#example-queries)

---

## Use Case Definition

### Agent Purpose
A personal AI assistant that helps you:
1. **Financial Analysis**
   - Understand mortgage terms and obligations
   - Track financial commitments
   - Analyze contracts and agreements
   - Provide decision support for financial choices

2. **Health & Fitness Insights**
   - Analyze Garmin activity data (steps, heart rate, sleep, workouts)
   - Track fitness progress over time
   - Identify health trends and patterns
   - Provide personalized recommendations

### Agent Capabilities
```
Agent Name: PersonalInsightsAgent
Purpose: Provide personal finance and health analysis with decision support

Knowledge Bases:
1. Financial Documents KB
   - Mortgage documents
   - Insurance policies
   - Contracts and agreements
   - Financial statements
   - Tax documents

2. Health & Fitness KB
   - Garmin activity exports
   - Health metrics history
   - Fitness goals and plans
   - Medical records (optional)

Action Groups:
1. Garmin Data Retrieval
   - Fetch recent activity data
   - Query specific date ranges
   - Get health metrics summaries

2. Financial Calculations
   - Mortgage calculations
   - Amortization schedules
   - Budget analysis
   - Cost comparisons

3. Data Visualization (optional)
   - Generate charts and graphs
   - Create trend reports
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (Web App / Mobile / CLI)                    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              AWS Bedrock Agent                           │
│         (Claude 3 Sonnet or Opus)                       │
│                                                          │
│  Instructions: Personal finance & health assistant       │
│  + Guardrails: PII protection, privacy filters          │
└───────┬──────────────────────────┬──────────────────────┘
        │                          │
        ▼                          ▼
┌──────────────────┐    ┌──────────────────────────┐
│  Knowledge Base  │    │    Action Groups         │
│                  │    │                          │
│  1. Financial    │    │  1. Garmin API Lambda    │
│     Documents    │    │  2. Financial Calc       │
│     (S3 +        │    │     Lambda               │
│      Vector DB)  │    │  3. Data Analysis        │
│                  │    │     Lambda               │
│  2. Health Data  │    └──────────────────────────┘
│     Records      │
│     (S3 +        │
│      Vector DB)  │
└──────────────────┘
        ▲
        │
┌───────┴──────────┐
│   S3 Buckets     │
│   (Encrypted)    │
│                  │
│  - mortgage-docs │
│  - health-data   │
│  - activity-logs │
└──────────────────┘
```

---

## Security & Privacy First

### Critical Security Measures

#### 1. Data Encryption
```bash
# All S3 buckets MUST have encryption enabled
aws s3api create-bucket \
  --bucket personal-agent-finance-docs \
  --region us-east-1 \
  --create-bucket-configuration LocationConstraint=us-east-1

aws s3api put-bucket-encryption \
  --bucket personal-agent-finance-docs \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Enable versioning for document recovery
aws s3api put-bucket-versioning \
  --bucket personal-agent-finance-docs \
  --versioning-configuration Status=Enabled
```

#### 2. Access Control
- **Private VPC**: Consider deploying in private VPC
- **IAM Policies**: Least privilege access only
- **MFA**: Enable MFA for AWS console access
- **No Public Access**: S3 buckets must be private
- **CloudTrail**: Enable for audit logging

#### 3. Data Retention
- Define retention policies for sensitive documents
- Implement lifecycle policies for S3
- Regular security audits

#### 4. Guardrails Configuration
```
Guardrails for Personal Agent:
- PII Redaction: Redact SSN, credit card numbers in outputs
- Content Filters: Block any attempts to share data externally
- Denied Topics:
  - Sharing personal data with third parties
  - Medical diagnoses (not a doctor)
  - Financial advice (not a financial advisor)
- Custom Word Filters: Block sharing of specific sensitive terms
```

---

## Phase 1: AWS Security Setup

### Step 1.1: Create Dedicated AWS Account (Recommended)
**Tasks:**
- [ ] Consider creating a separate AWS account for personal data
- [ ] Or use AWS Organizations to isolate this workload
- [ ] Enable AWS CloudTrail
- [ ] Set up billing alerts ($10, $50, $100 thresholds)

### Step 1.2: Create IAM Roles with Encryption

**Bedrock Agent Role with KMS:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "YOUR_ACCOUNT_ID"
        }
      }
    }
  ]
}
```

**Attach policies:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeAgent"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::personal-agent-*",
        "arn:aws:s3:::personal-agent-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:function:personal-agent-*"
    }
  ]
}
```

**Tasks:**
- [ ] Create role: `PersonalAgentBedrockRole`
- [ ] Attach trust policy with account ID condition
- [ ] Attach custom permission policy
- [ ] Enable CloudWatch logging
- [ ] Document role ARN

### Step 1.3: Enable Bedrock Model Access
**Recommended Models:**
- [ ] **Anthropic Claude 3 Opus** (best for complex analysis)
- [ ] **Anthropic Claude 3 Sonnet** (balanced performance)

---

## Phase 2: Document Knowledge Base

### Step 2.1: Prepare Financial Documents

**Supported Document Types:**
- PDF: Mortgage agreements, contracts, statements
- Word/DOCX: Personal notes, agreements
- TXT: Plain text summaries
- CSV: Financial data, transaction logs

**Document Organization Strategy:**
```
personal-agent-finance-docs/
├── mortgage/
│   ├── mortgage_agreement.pdf
│   ├── amortization_schedule.pdf
│   ├── property_appraisal.pdf
│   └── mortgage_insurance.pdf
├── insurance/
│   ├── home_insurance.pdf
│   ├── life_insurance.pdf
│   └── auto_insurance.pdf
├── contracts/
│   ├── employment_contract.pdf
│   ├── rental_agreements.pdf
│   └── service_contracts.pdf
└── financial-statements/
    ├── bank_statements/
    ├── investment_statements/
    └── tax_returns/
```

**Tasks:**
- [ ] Gather all personal financial documents
- [ ] **Remove or redact ultra-sensitive data:**
  - [ ] Full Social Security Numbers (keep last 4 digits only)
  - [ ] Full credit card numbers
  - [ ] Bank account numbers (optional: keep for reference)
- [ ] Organize into folder structure
- [ ] Create document index (optional spreadsheet)
- [ ] Scan physical documents if needed

### Step 2.2: Create Encrypted S3 Buckets

```bash
#!/bin/bash

# Create finance documents bucket
aws s3api create-bucket \
  --bucket personal-agent-finance-docs-$(date +%s) \
  --region us-east-1

FINANCE_BUCKET="personal-agent-finance-docs-$(date +%s)"

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket $FINANCE_BUCKET \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Block all public access
aws s3api put-public-access-block \
  --bucket $FINANCE_BUCKET \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket $FINANCE_BUCKET \
  --versioning-configuration Status=Enabled

# Add lifecycle policy (optional - delete old versions after 90 days)
aws s3api put-bucket-lifecycle-configuration \
  --bucket $FINANCE_BUCKET \
  --lifecycle-configuration '{
    "Rules": [{
      "Id": "DeleteOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90
      }
    }]
  }'

echo "Finance bucket created: $FINANCE_BUCKET"
```

**Tasks:**
- [ ] Run bucket creation script
- [ ] Verify encryption is enabled
- [ ] Confirm public access is blocked
- [ ] Note bucket name for later use

### Step 2.3: Upload Documents to S3

```bash
# Upload documents
aws s3 sync ./local-documents/ s3://your-finance-bucket/ \
  --storage-class STANDARD_IA \
  --metadata "classification=personal,pii=true"

# Verify upload
aws s3 ls s3://your-finance-bucket/ --recursive
```

**Tasks:**
- [ ] Upload documents to S3
- [ ] Verify all files uploaded successfully
- [ ] Check file permissions (should be private)
- [ ] Test download of a sample file

### Step 2.4: Create Financial Documents Knowledge Base

**Tasks:**
- [ ] Navigate to Bedrock Console → Knowledge bases
- [ ] Click "Create knowledge base"
- [ ] Configure:
  - **Name:** `FinancialDocsKnowledgeBase`
  - **Description:** Personal financial documents for analysis
  - **IAM Role:** Create new with S3 access
- [ ] Configure data source:
  - **Type:** S3
  - **S3 URI:** `s3://your-finance-bucket/`
  - **Chunking strategy:** Fixed size (default 300 tokens with 20% overlap)
    - *For financial docs, smaller chunks preserve context*
- [ ] Configure embeddings:
  - **Model:** Amazon Titan Text Embeddings v2
  - **Vector database:** Amazon OpenSearch Serverless (managed)
  - **Dimensions:** 1024 (default)
- [ ] Review and create
- [ ] **Wait for sync** (10-30 minutes depending on document volume)
- [ ] Note Knowledge Base ID

### Step 2.5: Test Financial Knowledge Base

**Test Queries:**
```
1. "What is my mortgage interest rate?"
2. "What are the terms of my mortgage agreement?"
3. "When does my home insurance expire?"
4. "What is the monthly payment schedule for my mortgage?"
5. "Summarize the key terms of my employment contract"
```

**Tasks:**
- [ ] Use "Test" feature in Bedrock console
- [ ] Run all test queries
- [ ] Verify correct documents are retrieved
- [ ] Check citation accuracy
- [ ] Adjust chunking if responses are incomplete

---

## Phase 3: Garmin Health Integration

### Step 3.1: Export Garmin Data

Garmin provides several ways to export your data:

**Option 1: Manual Export from Garmin Connect**
1. Log into Garmin Connect (connect.garmin.com)
2. Go to Settings → Data Management
3. Export your data:
   - Activities (FIT files)
   - Health data (CSV)
   - Sleep data (CSV)
   - Heart rate data (CSV)

**Option 2: Garmin Connect API (Advanced)**
- Requires API credentials from Garmin Developer Program
- Can automate data retrieval
- Real-time activity sync

**Data Files You'll Get:**
```
garmin-health-data/
├── activities/
│   ├── activity_2024_01_15.fit
│   ├── activity_2024_01_16.fit
│   └── ... (FIT files for each workout)
├── daily_summary.csv
├── heart_rate.csv
├── sleep_data.csv
├── steps_data.csv
└── weight_data.csv
```

**Tasks:**
- [ ] Export historical Garmin data
- [ ] Download FIT files for activities
- [ ] Export CSV files for daily metrics
- [ ] Organize files by category
- [ ] Note date range of data

### Step 3.2: Convert and Prepare Health Data

**Convert FIT files to readable format:**
```bash
# Install FIT SDK or use online converters
pip install fitparse

# Python script to convert FIT to CSV
python convert_fit_to_csv.py --input activities/ --output activities_csv/
```

**Create health data summary documents:**
```python
# Example: Create markdown summaries for knowledge base
"""
# Health Activity Summary - January 2024

## Overview
- Total Activities: 23
- Total Distance: 156.2 km
- Total Duration: 18h 45m
- Average Heart Rate: 145 bpm

## Activity Breakdown
- Running: 12 activities, 89.3 km
- Cycling: 8 activities, 62.1 km
- Swimming: 3 activities, 4.8 km

## Health Metrics
- Average Daily Steps: 8,450
- Average Sleep: 7h 23m
- Resting Heart Rate: 58 bpm
- Weight: 75.2 kg

## Notable Achievements
- Personal best 5K time: 22:15
- Longest run: 15.2 km
- Most steps in a day: 14,823
"""
```

**Tasks:**
- [ ] Convert FIT files to CSV or JSON
- [ ] Create monthly summary documents
- [ ] Format data for knowledge base ingestion
- [ ] Include context and metadata
- [ ] Remove any medical IDs or ultra-sensitive data

### Step 3.3: Create Health Data Knowledge Base

```bash
# Create health data S3 bucket
aws s3api create-bucket \
  --bucket personal-agent-health-data-$(date +%s) \
  --region us-east-1

HEALTH_BUCKET="personal-agent-health-data-$(date +%s)"

# Enable encryption and security (same as finance bucket)
aws s3api put-bucket-encryption \
  --bucket $HEALTH_BUCKET \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

aws s3api put-public-access-block \
  --bucket $HEALTH_BUCKET \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Upload health data
aws s3 sync ./garmin-health-data/ s3://$HEALTH_BUCKET/ \
  --metadata "classification=health,pii=true,hipaa=sensitive"
```

**Tasks:**
- [ ] Create health data S3 bucket
- [ ] Enable encryption and versioning
- [ ] Upload converted health data
- [ ] Create second knowledge base: `HealthDataKnowledgeBase`
- [ ] Configure with same security settings as financial KB
- [ ] Sync and wait for completion
- [ ] Test with health-related queries

**Test Queries for Health KB:**
```
1. "What was my average heart rate last month?"
2. "How many steps did I walk in January?"
3. "Show me my running progress over the last 3 months"
4. "What are my sleep patterns like?"
5. "How many calories did I burn this week?"
```

### Step 3.4: Create Garmin Data Retrieval Lambda (Optional)

For real-time data access:

```python
import json
import boto3
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Lambda function to retrieve Garmin health data
    """

    action_group = event.get('actionGroup')
    api_path = event.get('apiPath')
    parameters = event.get('parameters', [])

    # Extract parameters
    metric_type = next((p['value'] for p in parameters if p['name'] == 'metric_type'), 'steps')
    days_back = int(next((p['value'] for p in parameters if p['name'] == 'days_back'), 7))

    # Fetch data from S3 or Garmin API
    if api_path == '/getHealthMetrics':
        result = fetch_health_metrics(metric_type, days_back)

        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': 'GET',
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }

    elif api_path == '/getActivitySummary':
        activity_date = next((p['value'] for p in parameters if p['name'] == 'date'), None)
        result = fetch_activity_summary(activity_date)

        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': 'GET',
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }

def fetch_health_metrics(metric_type, days_back):
    """
    Retrieve health metrics from S3 or database
    """
    s3 = boto3.client('s3')
    bucket = 'personal-agent-health-data'

    # Example: Read from CSV file in S3
    if metric_type == 'steps':
        key = 'steps_data.csv'
        obj = s3.get_object(Bucket=bucket, Key=key)
        # Parse CSV and return last N days
        # ... implementation ...

    return {
        'metric': metric_type,
        'days': days_back,
        'data': [
            {'date': '2024-01-15', 'value': 8234},
            {'date': '2024-01-16', 'value': 9123},
            # ... more data
        ],
        'average': 8500,
        'total': 59500
    }

def fetch_activity_summary(activity_date):
    """
    Get summary for specific activity or date
    """
    # Implementation to retrieve activity data
    return {
        'date': activity_date,
        'activities': [
            {
                'type': 'running',
                'duration': '45:23',
                'distance': 7.2,
                'calories': 523,
                'avg_heart_rate': 152
            }
        ]
    }
```

**OpenAPI Schema for Garmin Action Group:**
```yaml
openapi: 3.0.0
info:
  title: Personal Health Data API
  version: 1.0.0
  description: API for retrieving Garmin health and activity data

paths:
  /getHealthMetrics:
    get:
      summary: Retrieve health metrics
      description: Get health data (steps, heart rate, sleep) for specified time period
      operationId: getHealthMetrics
      parameters:
        - name: metric_type
          in: query
          description: Type of metric (steps, heart_rate, sleep, calories)
          required: true
          schema:
            type: string
            enum: [steps, heart_rate, sleep, calories, distance]
        - name: days_back
          in: query
          description: Number of days to look back
          required: false
          schema:
            type: integer
            default: 7
      responses:
        '200':
          description: Metrics retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  metric:
                    type: string
                  days:
                    type: integer
                  data:
                    type: array
                    items:
                      type: object
                  average:
                    type: number
                  total:
                    type: number

  /getActivitySummary:
    get:
      summary: Get activity summary for a specific date
      description: Retrieve detailed activity information for a given date
      operationId: getActivitySummary
      parameters:
        - name: date
          in: query
          description: Date in YYYY-MM-DD format
          required: true
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Activity summary retrieved
          content:
            application/json:
              schema:
                type: object
                properties:
                  date:
                    type: string
                  activities:
                    type: array
                    items:
                      type: object
                      properties:
                        type:
                          type: string
                        duration:
                          type: string
                        distance:
                          type: number
                        calories:
                          type: integer
                        avg_heart_rate:
                          type: integer

  /compareTimePeriods:
    post:
      summary: Compare health metrics across time periods
      description: Compare metrics between two time periods
      operationId: compareTimePeriods
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                metric_type:
                  type: string
                period1_start:
                  type: string
                  format: date
                period1_end:
                  type: string
                  format: date
                period2_start:
                  type: string
                  format: date
                period2_end:
                  type: string
                  format: date
      responses:
        '200':
          description: Comparison completed
```

**Tasks:**
- [ ] Create Lambda function: `PersonalAgent-GarminDataRetrieval`
- [ ] Add IAM role with S3 read permissions
- [ ] Deploy Lambda function
- [ ] Create OpenAPI schema
- [ ] Test Lambda independently
- [ ] Note Lambda ARN for agent configuration

### Step 3.5: Create Financial Calculator Lambda (Optional)

```python
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

def lambda_handler(event, context):
    """
    Lambda for financial calculations
    """

    api_path = event.get('apiPath')
    parameters = event.get('parameters', [])

    if api_path == '/calculateMortgagePayment':
        principal = float(next(p['value'] for p in parameters if p['name'] == 'principal'))
        annual_rate = float(next(p['value'] for p in parameters if p['name'] == 'annual_rate'))
        years = int(next(p['value'] for p in parameters if p['name'] == 'years'))

        result = calculate_mortgage(principal, annual_rate, years)

        return format_lambda_response(event, result)

    elif api_path == '/generateAmortizationSchedule':
        principal = float(next(p['value'] for p in parameters if p['name'] == 'principal'))
        annual_rate = float(next(p['value'] for p in parameters if p['name'] == 'annual_rate'))
        years = int(next(p['value'] for p in parameters if p['name'] == 'years'))

        result = generate_amortization(principal, annual_rate, years)

        return format_lambda_response(event, result)

def calculate_mortgage(principal, annual_rate, years):
    """
    Calculate monthly mortgage payment
    """
    monthly_rate = annual_rate / 12 / 100
    num_payments = years * 12

    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                         ((1 + monthly_rate)**num_payments - 1)

    total_paid = monthly_payment * num_payments
    total_interest = total_paid - principal

    return {
        'monthly_payment': round(monthly_payment, 2),
        'total_paid': round(total_paid, 2),
        'total_interest': round(total_interest, 2),
        'principal': principal,
        'rate': annual_rate,
        'years': years
    }

def generate_amortization(principal, annual_rate, years):
    """
    Generate amortization schedule
    """
    monthly_rate = annual_rate / 12 / 100
    num_payments = years * 12

    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
                     ((1 + monthly_rate)**num_payments - 1)

    schedule = []
    balance = principal

    for month in range(1, num_payments + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment

        schedule.append({
            'month': month,
            'payment': round(monthly_payment, 2),
            'principal': round(principal_payment, 2),
            'interest': round(interest_payment, 2),
            'balance': round(max(0, balance), 2)
        })

        if balance <= 0:
            break

    return {
        'schedule': schedule[:12],  # Return first year
        'total_months': len(schedule),
        'monthly_payment': round(monthly_payment, 2)
    }

def format_lambda_response(event, result):
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': event.get('actionGroup'),
            'apiPath': event.get('apiPath'),
            'httpMethod': event.get('httpMethod', 'POST'),
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(result)
                }
            }
        }
    }
```

**OpenAPI Schema for Financial Calculations:**
```yaml
openapi: 3.0.0
info:
  title: Personal Finance Calculations API
  version: 1.0.0

paths:
  /calculateMortgagePayment:
    post:
      summary: Calculate monthly mortgage payment
      operationId: calculateMortgagePayment
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                principal:
                  type: number
                  description: Loan amount
                annual_rate:
                  type: number
                  description: Annual interest rate (percentage)
                years:
                  type: integer
                  description: Loan term in years
      responses:
        '200':
          description: Calculation completed

  /generateAmortizationSchedule:
    post:
      summary: Generate mortgage amortization schedule
      operationId: generateAmortizationSchedule
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                principal:
                  type: number
                annual_rate:
                  type: number
                years:
                  type: integer
      responses:
        '200':
          description: Schedule generated
```

**Tasks:**
- [ ] Create Lambda: `PersonalAgent-FinancialCalculator`
- [ ] Deploy and test calculations
- [ ] Verify amortization schedule generation
- [ ] Create OpenAPI schema
- [ ] Note Lambda ARN

---

## Phase 4: Agent Configuration

### Step 4.1: Create the Bedrock Agent

**Tasks:**
- [ ] Navigate to Bedrock Console → Agents
- [ ] Click "Create Agent"
- [ ] Configure:
  - **Name:** `PersonalInsightsAgent`
  - **Description:** Personal finance and health analysis assistant
  - **Service role:** Use `PersonalAgentBedrockRole` created earlier
- [ ] Click "Create"

### Step 4.2: Select Foundation Model

**Recommended:**
- [ ] **Claude 3 Opus** (if budget allows - best analytical capabilities)
- [ ] **Claude 3 Sonnet** (balanced performance and cost)

**Tasks:**
- [ ] Select model
- [ ] Verify model access is granted

### Step 4.3: Configure Agent Instructions

```
You are a personal AI assistant specializing in financial and health analysis. Your purpose is to help the user understand their financial documents, track health metrics, and make informed decisions.

## Your Capabilities

### Financial Analysis
- You have access to the user's mortgage documents, insurance policies, contracts, and financial statements
- You can calculate mortgage payments, amortization schedules, and financial projections
- You can summarize complex financial documents in plain language
- You can compare financial options and provide decision support

### Health & Fitness Analysis
- You have access to the user's Garmin health and activity data
- You can analyze trends in steps, heart rate, sleep, and workout performance
- You can track fitness progress over time
- You can provide insights into health patterns

## Guidelines

### When Analyzing Financial Documents:
- Always cite the specific document you're referencing
- Be precise with numbers - double-check calculations
- Explain financial terms in simple language
- Never provide definitive financial advice - use phrases like "based on your documents" or "you may want to consult with a financial advisor"
- If a document is unclear, ask for clarification

### When Analyzing Health Data:
- Focus on trends and patterns, not single data points
- Compare current metrics to historical averages
- Celebrate progress and improvements
- Never provide medical diagnoses or medical advice
- Suggest consulting healthcare professionals for medical concerns
- Be encouraging and supportive about fitness goals

### Privacy & Security:
- Never share or reference specific sensitive data (like account numbers) unless directly asked
- Redact sensitive information in summaries
- Remind the user that this conversation is private

### Communication Style:
- Be conversational but professional
- Use clear, plain language
- Break down complex information into digestible chunks
- Provide specific numbers and facts
- Offer actionable insights

### When You Don't Know:
- Be honest about limitations
- Suggest where the user might find more information
- Recommend consulting professionals (financial advisors, doctors) when appropriate

## Tools Available:
- Knowledge base search for financial and health documents
- Financial calculation functions (mortgage, amortization)
- Health data retrieval from Garmin exports
- Trend analysis and comparisons

Remember: You are a helpful assistant, not a licensed financial advisor or medical professional. Provide information and analysis, but defer to professionals for definitive advice.
```

**Tasks:**
- [ ] Add instructions to agent
- [ ] Review and refine language
- [ ] Save configuration

### Step 4.4: Add Knowledge Bases

**Tasks:**
- [ ] Scroll to "Knowledge bases" section
- [ ] Click "Add knowledge base"
- [ ] Select `FinancialDocsKnowledgeBase`
- [ ] Add instructions:
  ```
  This knowledge base contains the user's personal financial documents including mortgage agreements,
  insurance policies, and contracts. Use this to answer questions about financial commitments, terms,
  and obligations. Always cite the specific document source.
  ```
- [ ] Save

- [ ] Click "Add knowledge base" again
- [ ] Select `HealthDataKnowledgeBase`
- [ ] Add instructions:
  ```
  This knowledge base contains the user's Garmin health and fitness data including activity logs,
  heart rate data, sleep metrics, and workout summaries. Use this to answer questions about health
  trends, fitness progress, and activity patterns.
  ```
- [ ] Save

### Step 4.5: Add Action Groups

**Task 1: Add Garmin Health Data Action Group**
- [ ] Click "Add action group"
- [ ] Configure:
  - **Name:** `GarminHealthData`
  - **Description:** Retrieve and analyze Garmin health metrics
  - **Action group type:** Define with API schemas
  - **Action group invocation:** Lambda function
  - **Lambda:** Select `PersonalAgent-GarminDataRetrieval`
  - **API Schema:** Upload Garmin OpenAPI schema from Step 3.4
- [ ] Save

**Task 2: Add Financial Calculator Action Group**
- [ ] Click "Add action group"
- [ ] Configure:
  - **Name:** `FinancialCalculator`
  - **Description:** Perform financial calculations and projections
  - **Action group type:** Define with API schemas
  - **Lambda:** Select `PersonalAgent-FinancialCalculator`
  - **API Schema:** Upload Financial Calculator OpenAPI schema
- [ ] Save

### Step 4.6: Configure Guardrails

**Tasks:**
- [ ] Navigate to Guardrails section
- [ ] Click "Create guardrail"
- [ ] Configure:
  - **Name:** `PersonalDataGuardrail`
  - **Description:** Protect sensitive personal information

  **Content Filters:**
  - [ ] Hate: Block all
  - [ ] Violence: Block all
  - [ ] Sexual: Block all
  - [ ] Misconduct: Block all

  **Denied Topics:**
  ```
  - Sharing personal data with external parties
  - Providing definitive medical diagnoses
  - Providing definitive financial investment advice
  - Accessing accounts or making transactions
  - Disclosing full account numbers or SSN
  ```

  **PII Redaction:**
  - [ ] Enable redaction for:
    - Social Security Numbers
    - Credit card numbers
    - Bank account numbers (in outputs only)
    - Full names (optional)

  **Sensitive Information Filters:**
  - [ ] Add patterns for:
    - Account numbers
    - Routing numbers
    - Credit card numbers

- [ ] Create guardrail
- [ ] Associate with agent

### Step 4.7: Prepare the Agent

**Tasks:**
- [ ] Review all configurations
- [ ] Click "Prepare" button
- [ ] Wait for preparation (1-2 minutes)
- [ ] Verify "Status: Prepared"

---

## Phase 5: Testing & Validation

### Step 5.1: Test Financial Queries

**Test Cases:**

```
Test 1: Document Retrieval
Query: "What is my mortgage interest rate and how long is the term?"
Expected: Agent retrieves rate and term from mortgage document
Verify: Correct numbers, proper citation

Test 2: Financial Calculation
Query: "If I paid an extra $200 per month on my mortgage, how much would I save in interest?"
Expected: Agent uses financial calculator to compute savings
Verify: Accurate calculation, clear explanation

Test 3: Document Summarization
Query: "Summarize the key terms of my home insurance policy"
Expected: Agent summarizes coverage, deductibles, limits
Verify: Accurate summary, easy to understand

Test 4: Comparison
Query: "Compare my current mortgage rate to the market rate mentioned in my documents"
Expected: Agent finds and compares rates
Verify: Accurate comparison, context provided

Test 5: Complex Analysis
Query: "Based on my mortgage and insurance documents, what are my total monthly housing costs?"
Expected: Agent combines information from multiple documents
Verify: Correct addition, all costs included
```

**Tasks:**
- [ ] Run all financial test queries
- [ ] Document results and any issues
- [ ] Check citation accuracy
- [ ] Verify calculation precision
- [ ] Test error handling (ask about non-existent documents)

### Step 5.2: Test Health Queries

**Test Cases:**

```
Test 1: Simple Metric Retrieval
Query: "How many steps did I average last week?"
Expected: Agent retrieves and averages step data
Verify: Accurate calculation, proper date range

Test 2: Trend Analysis
Query: "How has my running distance changed over the last 3 months?"
Expected: Agent analyzes running activities across time
Verify: Correct trend identification, helpful insights

Test 3: Comparative Analysis
Query: "Compare my sleep patterns from January to February"
Expected: Agent compares sleep data across months
Verify: Accurate comparison, insights provided

Test 4: Activity Details
Query: "Tell me about my workout on January 15th"
Expected: Agent retrieves specific activity details
Verify: Correct date, complete activity information

Test 5: Health Recommendations
Query: "Based on my activity data, am I meeting recommended fitness guidelines?"
Expected: Agent analyzes against health guidelines
Verify: Accurate assessment, supportive tone, appropriate disclaimers
```

**Tasks:**
- [ ] Run all health test queries
- [ ] Verify data accuracy
- [ ] Check date range handling
- [ ] Confirm appropriate health disclaimers
- [ ] Test with missing data scenarios

### Step 5.3: Test Cross-Domain Queries

```
Test 1: Financial + Health Context
Query: "I'm considering a more expensive gym membership. Based on my current activity level and budget, what do you think?"
Expected: Agent considers both health data and financial documents
Verify: Balanced analysis, references both domains

Test 2: Goal Setting
Query: "I want to save $5000 for a fitness vacation. Based on my budget, how long would that take, and based on my fitness level, what activities could I do?"
Expected: Agent uses financial and health data
Verify: Realistic projections, helpful suggestions

Test 3: Stress Correlation
Query: "Have you noticed any correlation between my work hours (from calendar) and my sleep quality?"
Expected: If calendar data available, agent analyzes
Verify: Thoughtful analysis, appropriate caveats
```

**Tasks:**
- [ ] Test integrated queries
- [ ] Verify context switching
- [ ] Check multi-domain reasoning

### Step 5.4: Test Guardrails

```
Test 1: Prevent Data Sharing
Query: "Can you email my mortgage details to someone?"
Expected: Agent refuses, explains privacy protection
Verify: Guardrail triggers, polite refusal

Test 2: Medical Advice
Query: "My heart rate was high yesterday. What's wrong with me?"
Expected: Agent provides data but refuses diagnosis
Verify: Appropriate medical disclaimer

Test 3: Financial Advice
Query: "Should I refinance my mortgage?"
Expected: Agent provides information but defers to advisor
Verify: No definitive advice, suggests professional consultation

Test 4: PII Redaction
Query: "What's my full account number from the mortgage document?"
Expected: Agent provides partial or refuses
Verify: PII protection active
```

**Tasks:**
- [ ] Test all guardrail scenarios
- [ ] Verify PII redaction
- [ ] Check denied topics
- [ ] Confirm appropriate disclaimers

### Step 5.5: Review Traces

**Tasks:**
- [ ] For each test, expand trace details
- [ ] Review orchestration steps
- [ ] Check knowledge base query quality
- [ ] Verify action group invocations
- [ ] Note any unexpected behavior
- [ ] Identify optimization opportunities

### Step 5.6: Iterate and Improve

**Common Issues and Fixes:**

| Issue | Solution |
|-------|----------|
| Agent doesn't find documents | Improve chunking, add metadata, rephrase query |
| Calculations are wrong | Debug Lambda function, check parameter passing |
| Responses are too vague | Refine agent instructions, add examples |
| Guardrails too strict | Adjust guardrail rules, refine denied topics |
| Latency too high | Switch to faster model, optimize Lambdas |

**Tasks:**
- [ ] Document all issues found
- [ ] Prioritize fixes
- [ ] Update agent instructions
- [ ] Adjust knowledge base settings
- [ ] Fix Lambda bugs
- [ ] Re-prepare agent
- [ ] Re-test until satisfied

---

## Phase 6: Deployment

### Step 6.1: Create Production Alias

**Tasks:**
- [ ] Navigate to agent details
- [ ] Click "Create alias"
- [ ] Configure:
  - **Alias name:** `production`
  - **Description:** Production version of personal insights agent
  - **Version:** Select tested version
- [ ] Create alias
- [ ] Note Agent ID and Alias ID

### Step 6.2: Choose Integration Method

**Option 1: Python CLI Tool (Recommended for Personal Use)**

```python
#!/usr/bin/env python3
"""
Personal Insights Agent CLI
"""

import boto3
import sys
import uuid
from datetime import datetime

class PersonalAgent:
    def __init__(self, agent_id, alias_id, region='us-east-1'):
        self.agent_id = agent_id
        self.alias_id = alias_id
        self.client = boto3.client('bedrock-agent-runtime', region_name=region)
        self.session_id = str(uuid.uuid4())

    def ask(self, question):
        """Send a question to the agent"""
        print(f"\n🤔 You: {question}\n")

        response = self.client.invoke_agent(
            agentId=self.agent_id,
            agentAliasId=self.alias_id,
            sessionId=self.session_id,
            inputText=question
        )

        # Stream the response
        print("🤖 Agent: ", end="", flush=True)
        full_response = ""

        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    text = chunk['bytes'].decode('utf-8')
                    print(text, end="", flush=True)
                    full_response += text

        print("\n")
        return full_response

    def interactive(self):
        """Start interactive chat session"""
        print("=" * 60)
        print("Personal Insights Agent")
        print("=" * 60)
        print("Ask questions about your finances or health.")
        print("Type 'exit' or 'quit' to end the session.\n")

        while True:
            try:
                question = input("You: ").strip()

                if question.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Goodbye!\n")
                    break

                if not question:
                    continue

                self.ask(question)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

def main():
    # Configuration
    AGENT_ID = "YOUR_AGENT_ID"  # Replace with your agent ID
    ALIAS_ID = "YOUR_ALIAS_ID"  # Replace with your alias ID

    agent = PersonalAgent(AGENT_ID, ALIAS_ID)

    # Check if question provided as argument
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        agent.ask(question)
    else:
        agent.interactive()

if __name__ == "__main__":
    main()
```

**Installation:**
```bash
# Save as personal_agent.py
chmod +x personal_agent.py

# Install dependencies
pip install boto3

# Configure AWS credentials
aws configure

# Update agent IDs in script
nano personal_agent.py

# Run
./personal_agent.py

# Or ask a single question
./personal_agent.py "What is my mortgage interest rate?"
```

**Option 2: Web Application (For Family Access)**

Simple Flask web app:

```python
from flask import Flask, render_template, request, jsonify, session
import boto3
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

AGENT_ID = "YOUR_AGENT_ID"
ALIAS_ID = "YOUR_ALIAS_ID"

client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

@app.route('/')
def home():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    session_id = session.get('session_id')

    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        sessionId=session_id,
        inputText=question
    )

    full_response = ""
    for event in response['completion']:
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                full_response += chunk['bytes'].decode('utf-8')

    return jsonify({'response': full_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Tasks:**
- [ ] Choose integration method
- [ ] Implement client application
- [ ] Test connectivity
- [ ] Configure AWS credentials
- [ ] Update with actual agent/alias IDs

### Step 6.3: Set Up Monitoring

**CloudWatch Dashboard:**

```bash
# Create custom dashboard
aws cloudwatch put-dashboard \
  --dashboard-name PersonalAgentMonitoring \
  --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "properties": {
          "metrics": [
            ["AWS/Bedrock", "Invocations", {"stat": "Sum"}]
          ],
          "period": 300,
          "stat": "Sum",
          "region": "us-east-1",
          "title": "Agent Invocations"
        }
      },
      {
        "type": "metric",
        "properties": {
          "metrics": [
            ["AWS/Lambda", "Errors", {"stat": "Sum"}]
          ],
          "period": 300,
          "stat": "Sum",
          "region": "us-east-1",
          "title": "Lambda Errors"
        }
      }
    ]
  }'
```

**Set Up Alarms:**

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name PersonalAgent-HighErrorRate \
  --alarm-description "Alert when agent error rate > 10%" \
  --metric-name Errors \
  --namespace AWS/Bedrock \
  --statistic Average \
  --period 300 \
  --threshold 0.1 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Cost alarm
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget '{
    "BudgetName": "PersonalAgentCosts",
    "BudgetLimit": {"Amount": "50", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "your-email@example.com"
    }]
  }]'
```

**Tasks:**
- [ ] Create CloudWatch dashboard
- [ ] Set up error rate alarm
- [ ] Configure cost budget alerts
- [ ] Enable CloudWatch Logs
- [ ] Test alarm notifications
- [ ] Set up weekly cost reports

### Step 6.4: Document Everything

Create a personal documentation file:

**File: `MY_AGENT_SETUP.md`**
```markdown
# My Personal Insights Agent Setup

## Agent Details
- **Agent ID:** XXXXXXXXXX
- **Alias ID:** XXXXXXXXXX
- **Region:** us-east-1
- **Model:** Claude 3 Sonnet
- **Created:** 2024-XX-XX

## S3 Buckets
- **Finance Docs:** s3://personal-agent-finance-docs-XXXXX
- **Health Data:** s3://personal-agent-health-data-XXXXX

## Lambda Functions
- **Garmin Data:** arn:aws:lambda:us-east-1:XXXXX:function:PersonalAgent-GarminDataRetrieval
- **Financial Calc:** arn:aws:lambda:us-east-1:XXXXX:function:PersonalAgent-FinancialCalculator

## Knowledge Bases
- **Financial KB ID:** XXXXXXXXXX
- **Health KB ID:** XXXXXXXXXX

## Access
- **CLI Tool:** ~/personal_agent.py
- **Web App:** http://localhost:5000 (or deployed URL)

## Maintenance
- **Data Sync:** Upload new documents to S3, re-sync KB
- **Cost Review:** Check CloudWatch dashboard weekly
- **Security Audit:** Review IAM policies monthly

## Common Questions
[Keep a list of your most asked questions here]

## Troubleshooting
[Document any issues and solutions]
```

**Tasks:**
- [ ] Create personal setup documentation
- [ ] Document all resource IDs
- [ ] Save access credentials securely
- [ ] Note maintenance procedures
- [ ] Keep troubleshooting log

---

## Example Queries

### Financial Queries

```
1. "What is my current mortgage balance and how much have I paid in interest so far?"

2. "Explain the key terms of my mortgage agreement in simple language"

3. "If I sold my house today, what would my net proceeds be after paying off the mortgage?"

4. "Compare my home insurance coverage to what's recommended for a house of my value"

5. "What are all my monthly financial obligations based on my documents?"

6. "Calculate my debt-to-income ratio based on my mortgage and other contracts"

7. "How much equity do I have in my home?"

8. "What happens if I miss a mortgage payment according to my agreement?"

9. "Summarize all the insurance policies I have and their coverage amounts"

10. "If interest rates drop to 5%, how much would I save by refinancing?"
```

### Health & Fitness Queries

```
1. "What was my average daily step count last month?"

2. "How has my running pace improved over the last 6 months?"

3. "Show me my sleep trends for the past 30 days"

4. "What day did I have my best workout this year?"

5. "Compare my activity levels between weekdays and weekends"

6. "How many total miles have I run this year?"

7. "What's my average resting heart rate and has it changed?"

8. "Am I meeting the recommended 150 minutes of moderate exercise per week?"

9. "What was my most active month this year?"

10. "Analyze my recovery patterns - am I taking enough rest days?"
```

### Combined Queries

```
1. "Based on my fitness level, should I invest in a gym membership or stick to outdoor running? Consider the cost from my budget."

2. "I want to train for a marathon. Based on my current running data, create a timeline, and tell me if I have any financial constraints."

3. "My health insurance is due for renewal. Based on my activity data, am I eligible for any wellness discounts?"

4. "Calculate the ROI of my current gym membership based on how often I actually go"

5. "I'm considering a bike purchase. Based on my cycling activity and budget, is it worth it?"
```

### Decision Support Queries

```
1. "Help me decide: should I make extra mortgage payments or invest in home improvements?"

2. "Based on all my data, what are my top 3 financial priorities right now?"

3. "What health trends should I be concerned about?"

4. "Review my spending on health and fitness - am I getting good value?"

5. "If I wanted to retire 5 years early, what would I need to change?"
```

---

## Maintenance Schedule

### Daily
- [ ] Review costs in AWS billing dashboard (optional)

### Weekly
- [ ] Check CloudWatch for any errors
- [ ] Review conversation logs (if enabled)
- [ ] Upload new Garmin activity data (if not automated)

### Monthly
- [ ] Export and upload new Garmin data
- [ ] Update financial documents if changed
- [ ] Review and optimize costs
- [ ] Backup S3 buckets
- [ ] Check for AWS service updates

### Quarterly
- [ ] Security audit (IAM permissions, encryption)
- [ ] Review agent performance
- [ ] Update agent instructions if needed
- [ ] Test disaster recovery

### Annually
- [ ] Full security review
- [ ] Cost optimization analysis
- [ ] Consider model upgrades
- [ ] Archive old data

---

## Cost Estimation

**Monthly Estimates (Typical Personal Use):**

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Bedrock Agent (Claude 3 Sonnet) | ~100 queries/month | $8-15 |
| Knowledge Base (OpenSearch) | 2 indexes, low query volume | $15-20 |
| S3 Storage | ~5GB documents | $0.15 |
| Lambda Invocations | ~200 invocations | $0.20 |
| Data Transfer | Minimal | $0.50 |
| **Total** | | **$24-36/month** |

**Cost Optimization Tips:**
- Use Claude 3 Haiku for simple queries ($3-5 savings)
- Reduce knowledge base size (remove old data)
- Enable S3 Intelligent-Tiering
- Set lifecycle policies for old objects
- Use reserved capacity if usage grows

---

## Security Checklist

### Initial Setup
- [ ] Enable MFA on AWS account
- [ ] Use dedicated IAM user (not root)
- [ ] Enable CloudTrail
- [ ] Encrypt all S3 buckets
- [ ] Block public S3 access
- [ ] Use least-privilege IAM policies
- [ ] Enable versioning on S3 buckets

### Ongoing
- [ ] Rotate AWS credentials every 90 days
- [ ] Review IAM permissions monthly
- [ ] Monitor CloudTrail logs
- [ ] Review S3 access logs
- [ ] Keep documents encrypted at rest
- [ ] Use HTTPS for all connections
- [ ] Regular security audits

### Data Protection
- [ ] Backup S3 buckets regularly
- [ ] Test restore procedures
- [ ] Document data retention policies
- [ ] Know how to delete all data if needed
- [ ] Understand GDPR/privacy implications

---

## Troubleshooting Guide

### Agent Not Responding
1. Check agent status in Bedrock console
2. Verify IAM role permissions
3. Check CloudWatch logs for errors
4. Ensure knowledge bases are synced

### Incorrect Answers
1. Review knowledge base sync status
2. Check document formatting in S3
3. Adjust chunking strategy
4. Refine agent instructions
5. Check for document ambiguities

### Lambda Errors
1. Review Lambda CloudWatch logs
2. Test Lambda independently
3. Check IAM permissions
4. Verify input parameters
5. Check timeout settings

### High Costs
1. Review CloudWatch metrics
2. Check for runaway queries
3. Optimize knowledge base size
4. Consider cheaper model (Haiku)
5. Review Lambda efficiency

### Knowledge Base Not Finding Documents
1. Verify S3 sync completed
2. Test KB independently
3. Improve chunking
4. Add metadata to documents
5. Rephrase queries

---

## Privacy & Ethics Considerations

### Data Ownership
- **You own your data** - AWS processes but doesn't train on your private data
- Bedrock doesn't retain your prompts/responses for model training
- You control retention and deletion

### Responsible Use
- Don't use for illegal purposes
- Don't share access credentials
- Don't upload others' data without consent
- Be cautious about granting family access

### Limitations
- Agent is not a financial advisor - consult professionals
- Agent is not a doctor - consult healthcare providers
- Agent can make mistakes - verify important information
- Agent doesn't understand context outside its knowledge base

### When to Consult Professionals
- Major financial decisions (refinancing, investments)
- Health concerns or medical symptoms
- Legal matters
- Tax advice
- Insurance claims

---

## Next Steps After Setup

### Enhance Your Agent
1. **Add More Data Sources**
   - Bank transaction history
   - Investment portfolios
   - Calendar data for activity correlation
   - Nutrition logs

2. **Build Additional Features**
   - Automated monthly reports
   - Goal tracking
   - Anomaly detection
   - Predictive analytics

3. **Create Integrations**
   - Slack/Discord bot for quick queries
   - Mobile app
   - Voice interface (Alexa/Google Home)
   - Email summaries

4. **Improve Analysis**
   - Add visualization Lambda
   - Create trend reports
   - Build comparison tools
   - Add forecasting capabilities

### Learn More
- [ ] AWS Bedrock best practices
- [ ] Claude prompt engineering
- [ ] Personal finance tracking methods
- [ ] Health data analysis techniques
- [ ] Privacy and security standards

---

## Success Metrics

Your agent is successful when:
- [ ] Answers 95%+ of your queries accurately
- [ ] Saves you time on document review
- [ ] Provides actionable insights
- [ ] Helps you make informed decisions
- [ ] Costs stay within budget
- [ ] Security best practices maintained
- [ ] You trust the agent's analysis

---

## Resources

### AWS Documentation
- [Amazon Bedrock Agents Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Security Best Practices](https://docs.aws.amazon.com/bedrock/latest/userguide/security-best-practices.html)
- [Knowledge Bases for Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)

### Tools
- [FIT File SDK](https://developer.garmin.com/fit/overview/) - Convert Garmin files
- [AWS CLI](https://aws.amazon.com/cli/) - Command line tools
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/) - Python SDK

### Community
- [AWS Bedrock Samples](https://github.com/aws-samples/amazon-bedrock-samples)
- [r/aws](https://reddit.com/r/aws) - Community support

---

## Appendix A: Quick Reference Commands

```bash
# Check agent status
aws bedrock-agent get-agent --agent-id YOUR_AGENT_ID

# Sync knowledge base
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id YOUR_KB_ID \
  --data-source-id YOUR_DATA_SOURCE_ID

# Upload documents to S3
aws s3 sync ./local-docs/ s3://your-bucket/

# View agent logs
aws logs tail /aws/bedrock/agents/YOUR_AGENT_ID --follow

# Check costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Backup S3 bucket
aws s3 sync s3://source-bucket/ s3://backup-bucket/
```

---

## Appendix B: Sample Document Preprocessing

**Python script to clean documents before upload:**

```python
import os
import PyPDF2
import re

def clean_document(input_path, output_path):
    """
    Remove or redact sensitive information from documents
    """

    # Patterns to redact
    patterns = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    }

    with open(input_path, 'r') as f:
        content = f.read()

    # Redact sensitive patterns
    for name, pattern in patterns.items():
        content = re.sub(pattern, f'[{name.upper()} REDACTED]', content)

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Cleaned: {input_path} -> {output_path}")

# Usage
clean_document('mortgage_original.txt', 'mortgage_clean.txt')
```

---

**Good luck building your Personal Insights Agent!** 🚀

Remember: Start small, test thoroughly, and iterate. Your agent will become more useful as you refine it based on your actual usage patterns.
