# Health Insights Agent - Comprehensive Implementation Plan

## Overview

A health coaching AI agent that integrates with Garmin Connect to provide personalized insights on swimming, running, and sleep performance. The agent acts as an expert swimming coach, master runner (10-20KM specialist), and sleep examination expert, powered by AWS Bedrock and Claude.

## Table of Contents

1. [System Architecture](#1-system-architecture-design)
2. [Garmin Connect Integration](#2-garmin-connect-integration-approach)
3. [Agent Implementation Strategy](#3-agent-implementation-strategy)
4. [RAG System Design](#4-rag-system-design-for-coaching-knowledge)
5. [Memory System](#5-memory-system-design)
6. [Data Flow Pipeline](#6-data-flow-and-processing-pipeline)
7. [Implementation Phases](#7-implementation-phases)
8. [Security & Privacy](#8-security-and-data-privacy-considerations)
9. [Cost Estimation](#9-cost-estimation)
10. [Risk Mitigation](#10-risk-mitigation)

---

## 1. System Architecture Design

### AWS Services Stack

**Core Agent Services:**
- **AWS Bedrock Agents** - Main agent orchestration with built-in tool calling and knowledge base integration
- **Amazon Bedrock Runtime** - Claude 3 Sonnet/Haiku for reasoning and coaching advice
- **Bedrock Knowledge Bases** - RAG implementation for coaching knowledge

**Data & Storage:**
- **Amazon DynamoDB** - Store user activity data, sleep metrics, and personalized coaching context
  - Tables: `UserProfiles`, `Activities`, `SleepData`, `CoachingHistory`, `UserMemory`
- **Amazon S3** - Store raw Garmin data dumps, coaching documents, and training plans
- **Amazon OpenSearch Serverless** - Vector store for RAG (managed by Bedrock Knowledge Base)

**Integration & Processing:**
- **AWS Lambda** - Multiple functions:
  - Garmin data fetcher (triggered by EventBridge)
  - Data transformation and normalization
  - Action group implementations for agent tools
  - API endpoints for user interactions
- **Amazon EventBridge** - Schedule Garmin data synchronization (e.g., every hour)
- **AWS Step Functions** - Orchestrate complex data processing workflows
- **Amazon API Gateway** - REST API for user Q&A interface

**Monitoring & Security:**
- **Amazon CloudWatch** - Logs, metrics, and alarms
- **AWS Secrets Manager** - Store Garmin Connect credentials securely
- **AWS IAM** - Fine-grained access control
- **Bedrock Guardrails** - Content filtering and safety controls

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  (Mobile App / Web Portal / Chat Interface)                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────────────┐
│              Amazon API Gateway + Lambda Authorizer              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                     AWS Bedrock Agent                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Agent Instructions: Swimming Coach + Runner + Sleep Expert│ │
│  │  Model: Claude 3 Sonnet                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  Knowledge Base  │  │  Action Groups   │  │   Guardrails  │ │
│  │  (RAG)           │  │  (Tools)         │  │               │ │
│  └────────┬─────────┘  └────────┬─────────┘  └───────────────┘ │
└───────────┼────────────────────┼─────────────────────────────────┘
            │                    │
            │                    │
┌───────────▼─────────┐  ┌───────▼──────────────────────────────┐
│  Bedrock KB         │  │     Lambda Action Groups             │
│  ┌────────────────┐ │  │  ┌────────────────────────────────┐ │
│  │ OpenSearch     │ │  │  │ getActivityData()              │ │
│  │ Serverless     │ │  │  │ getSwimmingStats()             │ │
│  └────────────────┘ │  │  │ getRunningMetrics()            │ │
│  ┌────────────────┐ │  │  │ getSleepAnalysis()             │ │
│  │ S3: Coaching   │ │  │  │ getUserGoals()                 │ │
│  │ Documents      │ │  │  │ saveCoachingAdvice()           │ │
│  └────────────────┘ │  │  │ generateTrainingPlan()         │ │
└─────────────────────┘  │  └────────────────────────────────┘ │
                         └────────────┬───────────────────────────┘
                                      │
                 ┌────────────────────┼───────────────────┐
                 │                    │                   │
┌────────────────▼────┐  ┌────────────▼────┐  ┌──────────▼────────┐
│   DynamoDB Tables   │  │   S3 Buckets    │  │  Garmin Connect   │
│  - Activities       │  │  - Raw Data     │  │  Integration      │
│  - SleepData        │  │  - Exports      │  │  ┌──────────────┐ │
│  - UserProfiles     │  │  - Backups      │  │  │ Lambda:      │ │
│  - CoachingHistory  │  │                 │  │  │ GarminFetcher│ │
│  - UserMemory       │  │                 │  │  └──────────────┘ │
└─────────────────────┘  └─────────────────┘  └───────────────────┘
                                                        ▲
                                                        │
                                              ┌─────────┴─────────┐
                                              │ EventBridge Rule  │
                                              │ (Hourly Trigger)  │
                                              └───────────────────┘
```

---

## 2. Garmin Connect Integration Approach

### Challenge

Garmin Connect doesn't have an official public API for third-party developers. We need a reliable data synchronization strategy.

### Recommended Approach (Three Options)

**Option A: Garmin Connect Python API (garminconnect library)** ⭐ **RECOMMENDED FOR POC**
- Use `garminconnect` Python library (unofficial but widely used)
- Authenticate with Garmin credentials
- Fetch activities, sleep data, and daily summaries
- Store in DynamoDB and S3

**Option B: Garmin Health API (Enterprise)**
- Requires business partnership with Garmin
- Official API with proper OAuth
- Best for production, but has approval process

**Option C: Export + Manual Upload (Fallback)**
- User exports data from Garmin Connect
- Uploads to S3 bucket
- Lambda processes and imports

### Implementation Details

```python
# Lambda Function: GarminDataFetcher
# Trigger: EventBridge (hourly or on-demand)
# Purpose: Fetch latest data from Garmin Connect

import boto3
from garminconnect import Garmin
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # 1. Get credentials from Secrets Manager
    secrets = get_garmin_credentials()

    # 2. Initialize Garmin Connect client
    client = Garmin(secrets['email'], secrets['password'])
    client.login()

    # 3. Fetch recent activities (last 24 hours)
    activities = client.get_activities(0, 50)  # Last 50 activities

    # 4. Process each activity type
    for activity in activities:
        activity_type = activity['activityType']['typeKey']

        if activity_type in ['lap_swimming', 'open_water_swimming']:
            process_swimming_activity(activity, client)
        elif activity_type in ['running', 'trail_running']:
            process_running_activity(activity, client)

    # 5. Fetch sleep data
    today = datetime.now()
    sleep_data = client.get_sleep_data(today.strftime('%Y-%m-%d'))
    process_sleep_data(sleep_data)

    # 6. Fetch daily steps
    steps_data = client.get_steps_data(today.strftime('%Y-%m-%d'))
    process_steps_data(steps_data)

    return {'statusCode': 200, 'body': 'Sync complete'}
```

### Data Schema in DynamoDB

**Activities Table:**
```json
{
  "userId": "user123",
  "activityId": "12345678",
  "timestamp": "2026-01-16T10:30:00Z",
  "activityType": "swimming",
  "duration": 3600,
  "distance": 2000,
  "metrics": {
    "poolLength": 25,
    "strokes": 1240,
    "swolf": 42,
    "avgPace": "1:48/100m",
    "avgHeartRate": 165,
    "avgPace": "5:20/km",
    "elevationGain": 120,
    "cadence": 175
  },
  "rawData": {}
}
```

**SleepData Table:**
```json
{
  "userId": "user123",
  "date": "2026-01-16",
  "totalSleep": 27000,
  "deepSleep": 7200,
  "lightSleep": 16200,
  "remSleep": 3600,
  "awakeTime": 900,
  "sleepScore": 82,
  "startTime": "2026-01-15T23:15:00Z",
  "endTime": "2026-01-16T07:00:00Z",
  "rawData": {}
}
```

---

## 3. Agent Implementation Strategy

### Agent Configuration

**Agent Name:** HealthInsightsCoach

**Agent Instructions:**
```
You are an expert health and fitness coach with specializations in:
1. Swimming Coach - Expert in pool swimming technique, training plans, and performance analysis
2. Master Runner (10-20KM) - Specialist in middle-distance running, pacing strategies, and race preparation
3. Sleep Expert - Certified sleep specialist focused on recovery and performance optimization

Your role is to:
- Analyze user's swimming, running, and sleep data from Garmin Connect
- Provide personalized coaching advice based on their actual performance metrics
- Answer questions about their training, technique, and recovery
- Generate adaptive training plans that balance swimming, running, and recovery
- Track progress over time and adjust recommendations accordingly

When analyzing data:
- Always reference specific metrics from their recent activities
- Look for patterns across multiple sessions
- Consider the interplay between training load and sleep quality
- Provide actionable, specific advice rather than generic tips

When you don't have data:
- Ask the user to sync their Garmin device
- Explain what data you need to provide better advice
- Offer general guidance while waiting for specific metrics

Use your tools to:
- Retrieve activity data for analysis
- Access sleep metrics to assess recovery
- Load user goals and preferences from memory
- Save important coaching insights for future reference
```

**Foundation Model:** Claude 3 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)

### Action Groups (Tools)

#### Action Group 1: ActivityDataRetrieval

```yaml
openapi: 3.0.0
info:
  title: Health Insights Activity Data API
  version: 1.0.0

paths:
  /activities/swimming/recent:
    get:
      summary: Get recent swimming activities
      operationId: getRecentSwimming
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
        - name: days
          in: query
          schema:
            type: integer
            default: 30
      responses:
        '200':
          description: List of swimming activities

  /activities/running/recent:
    get:
      summary: Get recent running activities
      operationId: getRecentRunning
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
        - name: days
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: List of running activities

  /sleep/analysis:
    get:
      summary: Get sleep analysis for date range
      operationId: getSleepAnalysis
      parameters:
        - name: startDate
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: endDate
          in: query
          required: true
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Sleep analysis data

  /steps/daily:
    get:
      summary: Get daily step counts
      operationId: getDailySteps
      parameters:
        - name: days
          in: query
          schema:
            type: integer
            default: 7
      responses:
        '200':
          description: Daily step data
```

#### Action Group 2: CoachingMemory

```yaml
paths:
  /memory/user-context:
    get:
      summary: Retrieve user context and goals
      operationId: getUserContext
      responses:
        '200':
          description: User goals, preferences, and history

  /memory/save-insight:
    post:
      summary: Save coaching insight to memory
      operationId: saveCoachingInsight
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                insight:
                  type: string
                category:
                  type: string
                  enum: [swimming, running, sleep, general]
      responses:
        '200':
          description: Insight saved

  /memory/training-plan:
    post:
      summary: Save or update training plan
      operationId: saveTrainingPlan
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                plan:
                  type: object
                startDate:
                  type: string
                  format: date
      responses:
        '200':
          description: Training plan saved
```

### Lambda Implementation for Action Groups

```python
# lambda/action_handler.py
import json
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
activities_table = dynamodb.Table('HealthInsights-Activities')
sleep_table = dynamodb.Table('HealthInsights-SleepData')
memory_table = dynamodb.Table('HealthInsights-UserMemory')

def lambda_handler(event, context):
    """
    Main handler for Bedrock Agent action groups
    """
    action_group = event.get('actionGroup')
    api_path = event.get('apiPath')
    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}

    # Route to appropriate handler
    if api_path == '/activities/swimming/recent':
        result = get_recent_swimming(parameters)
    elif api_path == '/activities/running/recent':
        result = get_recent_running(parameters)
    elif api_path == '/sleep/analysis':
        result = get_sleep_analysis(parameters)
    elif api_path == '/steps/daily':
        result = get_daily_steps(parameters)
    elif api_path == '/memory/user-context':
        result = get_user_context()
    elif api_path == '/memory/save-insight':
        result = save_coaching_insight(parameters)
    elif api_path == '/memory/training-plan':
        result = save_training_plan(parameters)
    else:
        result = {'error': 'Unknown API path'}

    return format_bedrock_response(action_group, api_path, result)

def get_recent_swimming(params):
    limit = int(params.get('limit', 10))
    days = int(params.get('days', 30))

    # Query DynamoDB
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    response = activities_table.query(
        IndexName='activityType-timestamp-index',
        KeyConditionExpression='activityType = :type AND #ts BETWEEN :start AND :end',
        ExpressionAttributeNames={'#ts': 'timestamp'},
        ExpressionAttributeValues={
            ':type': 'swimming',
            ':start': start_date.isoformat(),
            ':end': end_date.isoformat()
        },
        Limit=limit,
        ScanIndexForward=False
    )

    activities = response.get('Items', [])

    # Calculate summary statistics
    summary = {
        'totalDistance': sum(a['distance'] for a in activities),
        'totalDuration': sum(a['duration'] for a in activities),
        'avgSwolf': sum(a['metrics']['swolf'] for a in activities) / len(activities) if activities else 0,
        'sessionCount': len(activities)
    }

    return {'activities': activities, 'summary': summary}

def format_bedrock_response(action_group, api_path, result):
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
```

---

## 4. RAG System Design for Coaching Knowledge

### Knowledge Base Structure

**S3 Bucket Organization:**
```
health-insights-kb/
├── swimming/
│   ├── technique/
│   │   ├── freestyle-technique.pdf
│   │   ├── breathing-patterns.pdf
│   │   └── turns-and-finishes.pdf
│   ├── training/
│   │   ├── interval-training-guide.pdf
│   │   ├── endurance-building.pdf
│   │   └── swim-workouts-library.pdf
│   └── analysis/
│       ├── swolf-interpretation.pdf
│       └── pace-analysis.pdf
├── running/
│   ├── 10km-training/
│   │   ├── beginner-10k-plan.pdf
│   │   ├── intermediate-10k.pdf
│   │   └── race-day-strategy.pdf
│   ├── half-marathon/
│   │   ├── 20km-training-guide.pdf
│   │   └── long-run-strategies.pdf
│   ├── technique/
│   │   ├── running-form.pdf
│   │   ├── cadence-optimization.pdf
│   │   └── hill-training.pdf
│   └── injury-prevention/
│       └── recovery-protocols.pdf
└── sleep/
    ├── sleep-science-for-athletes.pdf
    ├── recovery-optimization.pdf
    ├── sleep-hygiene-guide.pdf
    └── sleep-metrics-interpretation.pdf
```

### Bedrock Knowledge Base Configuration

**Settings:**
- **Vector Database:** Amazon OpenSearch Serverless
- **Embedding Model:** amazon.titan-embed-text-v1
- **Chunking Strategy:** Fixed-size (300 tokens with 20% overlap)
- **Retrieval Configuration:** Top 5 results with score threshold 0.7

**Knowledge Base Instructions for Agent:**
```
Use this knowledge base to answer questions about:
- Swimming technique, training methods, and performance analysis
- Running training plans, pacing strategies, and form optimization
- Sleep science, recovery protocols, and sleep quality interpretation

When retrieving information:
1. Always cite the source document
2. Combine knowledge base information with user's actual data
3. Adapt general advice to the user's specific situation and metrics
4. If knowledge base doesn't have specific information, acknowledge limitations
```

---

## 5. Memory System Design

### Memory Architecture

**Layer 1: Session Memory (Bedrock Agent built-in)**
- Conversation history within current session
- Automatically managed by Bedrock Agents
- Retained for session duration (up to 1 hour)

**Layer 2: User Context Memory (DynamoDB)**

**Table:** `HealthInsights-UserMemory`

**Schema:**
```json
{
  "userId": "user123",
  "memoryType": "user_profile",
  "timestamp": "2026-01-16T10:30:00Z",
  "content": {},
  "ttl": 1704067200
}
```

**Example Entries:**

1. **User Profile:**
```json
{
  "userId": "user123",
  "memoryType": "user_profile",
  "content": {
    "name": "John",
    "age": 35,
    "swimmingLevel": "intermediate",
    "runningLevel": "advanced",
    "preferredPoolLength": 25,
    "goals": {
      "swimming": "Improve 100m freestyle time to under 1:30",
      "running": "Complete half marathon in under 1:45",
      "sleep": "Achieve 8 hours of sleep 5 nights per week"
    }
  }
}
```

2. **Coaching Insights:**
```json
{
  "userId": "user123",
  "memoryType": "coaching_insight",
  "timestamp": "2026-01-15T18:00:00Z",
  "content": {
    "category": "swimming",
    "insight": "User shows consistent improvement in SWOLF score, dropping from 45 to 42 over 2 weeks. This indicates better efficiency. Focus on maintaining this through stroke count drills.",
    "relatedActivities": ["act123", "act125", "act127"]
  }
}
```

3. **Training Plans:**
```json
{
  "userId": "user123",
  "memoryType": "training_plan",
  "timestamp": "2026-01-10T09:00:00Z",
  "content": {
    "planType": "running",
    "duration": "8 weeks",
    "goal": "Half Marathon under 1:45",
    "weeklyStructure": {},
    "currentWeek": 2,
    "compliance": 0.85
  }
}
```

**Layer 3: Long-term Analytics (S3 + Athena)**
- Historical data aggregations
- Trend analysis over months/years
- Queryable with Amazon Athena for deep insights

### Memory Retrieval Logic

```python
# Lambda function: get_user_context
def get_user_context():
    user_id = get_current_user_id()

    # Get user profile
    profile = memory_table.get_item(
        Key={'userId': user_id, 'memoryType': 'user_profile'}
    ).get('Item', {})

    # Get recent coaching insights (last 30 days)
    insights = memory_table.query(
        KeyConditionExpression='userId = :uid AND memoryType = :type',
        FilterExpression='#ts > :cutoff',
        ExpressionAttributeNames={'#ts': 'timestamp'},
        ExpressionAttributeValues={
            ':uid': user_id,
            ':type': 'coaching_insight',
            ':cutoff': (datetime.now() - timedelta(days=30)).isoformat()
        },
        Limit=10
    ).get('Items', [])

    # Get active training plans
    plans = memory_table.query(
        KeyConditionExpression='userId = :uid AND memoryType = :type',
        ExpressionAttributeValues={
            ':uid': user_id,
            ':type': 'training_plan'
        }
    ).get('Items', [])

    return {
        'profile': profile,
        'recentInsights': insights,
        'activePlans': plans
    }
```

---

## 6. Data Flow and Processing Pipeline

### Flow 1: Automated Data Synchronization

```
EventBridge (Hourly)
    → Lambda: GarminDataFetcher
        → Garmin Connect API
        → Lambda: DataTransformer
            → DynamoDB: Activities, SleepData
            → S3: Raw data backup
                → EventBridge: DataSyncComplete
                    → Lambda: TriggerAnalysis (optional)
```

### Flow 2: User Query Processing

```
User Question
    → API Gateway
        → Lambda: QueryHandler
            → Bedrock Agent: invoke_agent()
                ├→ Bedrock Knowledge Base (RAG)
                │    → OpenSearch Serverless
                │    → Returns relevant coaching docs
                │
                ├→ Action Group: getActivityData
                │    → Lambda: ActionHandler
                │    → DynamoDB: Activities
                │    → Returns recent metrics
                │
                └→ Action Group: getUserContext
                     → Lambda: ActionHandler
                     → DynamoDB: UserMemory
                     → Returns user goals, insights
            ← Bedrock Agent Response
        ← Format response
    ← User receives personalized coaching advice
```

### Flow 3: Proactive Insights (Optional Enhancement)

```
EventBridge (Daily at 8 AM)
    → Lambda: InsightGenerator
        → Query last 7 days of data
        → Bedrock: Generate weekly summary
        → SES or SNS: Send email/notification
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Set up AWS infrastructure and basic agent

**Tasks:**
1. Set up AWS environment
   - Configure IAM roles and policies
   - Create DynamoDB tables
   - Set up S3 buckets
   - Enable Bedrock model access (Claude 3 Sonnet)

2. Implement Garmin Connect integration
   - Create Lambda: GarminDataFetcher
   - Store credentials in Secrets Manager
   - Test data fetching for swimming, running, sleep, steps
   - Implement data transformation and storage

3. Create basic Bedrock Agent
   - Define agent with initial instructions
   - Create first action group: ActivityDataRetrieval
   - Implement Lambda action handler
   - Test agent with mock queries

**Success Criteria:**
- ✅ Garmin data syncs automatically to DynamoDB
- ✅ Agent can retrieve and discuss activity data
- ✅ Basic Q&A works: "What were my recent swimming sessions?"

### Phase 2: RAG Knowledge Base (Week 3)
**Goal:** Add coaching expertise through knowledge base

**Tasks:**
1. Collect and prepare coaching documents
   - Swimming technique guides
   - Running training plans
   - Sleep optimization resources
   - Convert to supported formats (PDF, TXT, MD)

2. Create Bedrock Knowledge Base
   - Upload documents to S3
   - Configure OpenSearch Serverless
   - Set up embeddings with Titan
   - Test retrieval quality

3. Integrate knowledge base with agent
   - Add knowledge base to agent configuration
   - Update agent instructions for KB usage
   - Test combined data + knowledge queries

**Success Criteria:**
- ✅ Agent can answer technique questions from knowledge base
- ✅ Agent combines KB knowledge with user's actual data
- ✅ Example: "How can I improve my freestyle technique? My current SWOLF is 42."

### Phase 3: Memory System (Week 4)
**Goal:** Personalized context and coaching continuity

**Tasks:**
1. Implement UserMemory table and operations
   - Create DynamoDB table schema
   - Implement memory save/retrieve functions
   - Create action group: CoachingMemory

2. Add memory integration to agent
   - Update agent instructions to use memory
   - Implement getUserContext() tool
   - Implement saveCoachingInsight() tool

3. Build user profile system
   - Capture user goals and preferences
   - Store coaching insights automatically
   - Maintain training plan state

**Success Criteria:**
- ✅ Agent remembers user goals across sessions
- ✅ Agent references previous insights: "Last week I noticed your SWOLF improved..."
- ✅ Coaching advice is personalized and consistent

### Phase 4: API & User Interface (Week 5)
**Goal:** User-facing interfaces

**Tasks:**
1. Build API Gateway integration
   - Create REST API endpoints
   - Implement Lambda: QueryHandler
   - Add authentication (Cognito or API keys)
   - Configure CORS

2. Create simple web interface
   - Chat interface for Q&A
   - Data dashboard showing recent activities
   - Goal setting and profile management

3. Implement session management
   - Handle multi-turn conversations
   - Maintain session state
   - Add conversation history view

**Success Criteria:**
- ✅ Users can ask questions via web interface
- ✅ Conversations feel natural and context-aware
- ✅ Users can view their activity summaries

### Phase 5: Advanced Features (Week 6-7)
**Goal:** Enhanced coaching capabilities

**Tasks:**
1. Training plan generation
   - Implement generateTrainingPlan() tool
   - Create adaptive plans based on current fitness
   - Track plan compliance

2. Advanced analytics
   - Trend analysis over time
   - Fatigue detection from sleep + training load
   - Performance predictions

3. Proactive insights
   - Daily/weekly summary notifications
   - Recovery recommendations
   - Race preparation reminders

**Success Criteria:**
- ✅ Agent generates personalized training plans
- ✅ Users receive proactive coaching insights
- ✅ Agent identifies patterns: "Your sleep quality drops after hard run workouts"

### Phase 6: Production Readiness (Week 8)
**Goal:** Security, monitoring, optimization

**Tasks:**
1. Security hardening
   - Implement Bedrock Guardrails
   - Add input validation
   - Audit IAM permissions
   - Enable encryption at rest

2. Monitoring and observability
   - CloudWatch dashboards
   - Alarms for errors and latency
   - Cost monitoring
   - Usage analytics

3. Performance optimization
   - Lambda cold start optimization
   - DynamoDB capacity tuning
   - Response caching where appropriate

4. Documentation
   - User guide
   - API documentation
   - Operational runbook

**Success Criteria:**
- ✅ System handles errors gracefully
- ✅ Response times < 5 seconds for simple queries
- ✅ All security best practices implemented
- ✅ Complete documentation

---

## 8. Security and Data Privacy Considerations

### Data Privacy

1. **Encryption**
   - All data encrypted at rest (DynamoDB, S3, OpenSearch)
   - TLS for all data in transit
   - Secrets Manager for credentials

2. **Access Control**
   - Principle of least privilege for all IAM roles
   - User data isolated by userId
   - API authentication required

3. **Data Retention**
   - Implement TTL for old data
   - User data deletion capability
   - Comply with GDPR/CCPA if applicable

4. **Sensitive Data**
   - No sharing of health data between users
   - Garmin credentials stored securely
   - No logging of PII in CloudWatch

### Bedrock Guardrails Configuration

```json
{
  "name": "HealthInsightsGuardrails",
  "description": "Safety controls for health coaching agent",
  "contentPolicyConfig": {
    "filtersConfig": [
      {"type": "HATE", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
      {"type": "VIOLENCE", "inputStrength": "MEDIUM", "outputStrength": "MEDIUM"},
      {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"}
    ]
  },
  "topicPolicyConfig": {
    "topicsConfig": [
      {
        "name": "MedicalDiagnosis",
        "definition": "Providing medical diagnoses or prescribing medications",
        "type": "DENY"
      },
      {
        "name": "InjuryDiagnosis",
        "definition": "Diagnosing injuries or medical conditions",
        "type": "DENY"
      }
    ]
  },
  "wordPolicyConfig": {
    "wordsConfig": [
      {"text": "guaranteed results"},
      {"text": "medical advice"}
    ]
  },
  "sensitiveInformationPolicyConfig": {
    "piiEntitiesConfig": [
      {"type": "EMAIL", "action": "ANONYMIZE"},
      {"type": "PHONE", "action": "ANONYMIZE"}
    ]
  }
}
```

### Compliance Considerations

- **Medical Disclaimer:** Agent should include disclaimer that it's not medical advice
- **Injury Detection:** If patterns suggest injury, recommend consulting healthcare professional
- **Data Ownership:** Users own their data, can export or delete
- **Audit Trail:** Log all agent interactions for accountability

---

## 9. Cost Estimation

### Monthly Costs (Single User Development/Testing)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Bedrock Claude 3 Sonnet | 500K tokens/month | ~$15 |
| Bedrock Knowledge Base | 10GB docs, 1K queries | ~$10 |
| DynamoDB | 5 tables, on-demand | ~$5 |
| Lambda | 10K invocations, 512MB | ~$2 |
| OpenSearch Serverless | 4 OCUs | ~$60 |
| S3 | 10GB storage, 1K requests | ~$1 |
| API Gateway | 10K requests | ~$0.50 |
| EventBridge | 720 events/month | <$1 |
| Secrets Manager | 3 secrets | ~$1.20 |
| **TOTAL** | | **~$95/month** |

### Cost Optimization Tips

- Use Claude 3 Haiku for simple queries (3x cheaper)
- Implement caching for common queries
- Use DynamoDB on-demand for dev, provisioned for production
- Consider OpenSearch alternatives (Pinecone free tier) for POC

---

## 10. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Garmin API changes/breaks | High | Implement fallback manual upload; monitor for library updates |
| High AWS costs | Medium | Set billing alarms; implement usage quotas; regular cost reviews |
| Agent provides harmful advice | High | Implement guardrails; add disclaimers; review agent responses |
| Data loss | Medium | Regular S3 backups; DynamoDB point-in-time recovery; version control |
| Slow response times | Medium | Optimize Lambda; cache frequent queries; use faster models when appropriate |
| Privacy breach | High | Encryption everywhere; IAM least privilege; regular security audits |

---

## Quick Start Guide

### Prerequisites
- AWS Account with Bedrock access enabled
- Garmin Connect account with activity data
- AWS CLI configured
- Python 3.11+ installed

### Step 1: Deploy Infrastructure
```bash
# Clone repository
git clone <repo-url>
cd health-insights-agent

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file infrastructure/template.yaml \
  --stack-name health-insights-agent \
  --capabilities CAPABILITY_IAM

# Store Garmin credentials
aws secretsmanager create-secret \
  --name health-insights/garmin-credentials \
  --secret-string '{"email":"your@email.com","password":"yourpassword"}'
```

### Step 2: Test Garmin Integration
```bash
# Invoke Garmin data fetcher manually
aws lambda invoke \
  --function-name GarminDataFetcher \
  --payload '{}' \
  response.json

# Check DynamoDB for data
aws dynamodb scan --table-name HealthInsights-Activities --limit 5
```

### Step 3: Create Bedrock Agent
```bash
# Use AWS Console or CLI to create agent
# See AWS_BEDROCK_AGENT_PLAN.md for detailed instructions
```

### Step 4: Test the Agent
```bash
# Invoke agent via API
curl -X POST https://your-api-gateway-url/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What were my swimming sessions this week?"}'
```

---

## Next Steps

1. **Review existing Bedrock Agent patterns** in `/home/user/MyFirstRepo/AWS_BEDROCK_AGENT_PLAN.md`
2. **Study memory implementation** in `/home/user/MyFirstRepo/Learning/lessons/07_memory.md`
3. **Start with Phase 1** - Foundation setup
4. **Document decisions** in a DECISIONS.md file

---

## Resources

- [AWS Bedrock Agents Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Garmin Connect Python Library](https://github.com/cyberjunky/python-garminconnect)
- [Existing AWS Agent Plan](/home/user/MyFirstRepo/AWS_BEDROCK_AGENT_PLAN.md)
- [Memory Patterns](/home/user/MyFirstRepo/Learning/lessons/07_memory.md)
- [Tool Implementation Guide](/home/user/MyFirstRepo/Learning/lessons/05_tools.md)

---

**Last Updated:** 2026-01-16
**Version:** 1.0
**Status:** Planning Phase
