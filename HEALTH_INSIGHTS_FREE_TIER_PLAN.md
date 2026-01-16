# Health Insights Agent - FREE TIER Personal Learning Plan

## 🎯 Project Goal

Build a personal health coaching AI agent for **learning purposes** using **AWS Free Tier** to minimize costs while understanding AI agent architecture, RAG systems, and AWS Bedrock.

**Target Cost:** $0-5/month (mostly free tier)
**Purpose:** Learning & personal use
**Scale:** Single user (you!)

---

## 📊 Cost-Optimized Architecture

### Free Tier Components

| Service | Free Tier Limit | Usage Plan | Monthly Cost |
|---------|----------------|------------|--------------|
| **DynamoDB** | 25GB storage, 25 RCU/WCU | Store activities, sleep, memory | **$0** (within free tier) |
| **Lambda** | 1M requests, 400K GB-seconds | All functions | **$0** (within free tier) |
| **S3** | 5GB (first 12 months), then pay | Documents, raw data | **$0-1** |
| **Bedrock Claude Haiku** | Pay per token | Minimize usage | **$2-5** |
| **Bedrock KB (Titan Embeddings)** | Pay per token + storage | Limited docs | **$0-2** |
| **EventBridge** | 14M events/month free | Hourly Garmin sync | **$0** |
| **Secrets Manager** | $0.40 per secret/month | Garmin credentials | **$0.40** |
| **API Gateway** | 1M requests free (first 12 months) | Optional web interface | **$0** |
| **CloudWatch** | 5GB logs, 10 metrics free | Basic monitoring | **$0** (within free tier) |
| **TOTAL** | | | **$2.40-8/month** |

### 🎉 Key Changes from Original Plan

**❌ REMOVED (Expensive):**
- OpenSearch Serverless ($60/month) → Use lightweight alternatives
- Claude Sonnet ($3/MTok) → Use Claude Haiku ($0.25/MTok) - 12x cheaper!
- Complex web UI → Simple CLI or minimal web page
- Multiple agent types → One simple agent

**✅ KEPT (Free/Cheap):**
- Bedrock Agent (learn agent orchestration)
- Garmin Connect integration (real data!)
- DynamoDB (free tier)
- Lambda (free tier)
- Knowledge Base with simplified RAG
- Memory system in DynamoDB

---

## 🏗️ Free Tier Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              User Interface (Choose One)                     │
│  Option A: CLI script (Python)                              │
│  Option B: Simple HTML page (S3 static hosting - free)     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Lambda: ChatHandler (Free Tier)                 │
│              Invoke Bedrock Agent                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              AWS Bedrock Agent                               │
│              Model: Claude 3 Haiku (12x cheaper!)           │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ Knowledge Base │  │ Action Group │  │  (No Guardrails│  │
│  │ (Simplified)   │  │ (2 tools)    │  │   for free)    │  │
│  └────────┬───────┘  └──────┬───────┘  └────────────────┘  │
└───────────┼──────────────────┼─────────────────────────────┘
            │                  │
            │                  │
    ┌───────▼────────┐  ┌──────▼──────────────────────────┐
    │ Bedrock KB     │  │ Lambda: ActionHandler           │
    │ Storage        │  │ (Free Tier)                     │
    │                │  │                                 │
    │ S3 Bucket      │  │ Tools:                          │
    │ + Titan        │  │ - getActivityData()             │
    │ Embeddings     │  │ - getUserContext()              │
    │                │  │                                 │
    │ (No OpenSearch)│  │                                 │
    └────────────────┘  └──────┬──────────────────────────┘
                               │
                    ┌──────────┼────────────┐
                    │          │            │
        ┌───────────▼─┐  ┌─────▼─────┐  ┌──▼──────────────┐
        │ DynamoDB    │  │ DynamoDB  │  │ Garmin Connect  │
        │ Activities  │  │ UserMemory│  │                 │
        │ SleepData   │  │           │  │ Lambda:         │
        │             │  │           │  │ GarminFetcher   │
        │ (Free Tier) │  │(Free Tier)│  │ (Free Tier)     │
        └─────────────┘  └───────────┘  └─────────────────┘
                                              ▲
                                              │
                                    ┌─────────┴──────────┐
                                    │ EventBridge        │
                                    │ (Hourly - Free)    │
                                    └────────────────────┘
```

---

## 🎓 Learning Objectives

By building this project, you'll learn:

1. **AI Agent Architecture**
   - How agents orchestrate multiple tools
   - When agents call tools vs knowledge base
   - Agent instruction engineering

2. **RAG (Retrieval Augmented Generation)**
   - Document chunking and embeddings
   - Vector similarity search
   - Combining retrieval with generation

3. **Memory Systems**
   - Short-term (session) memory
   - Long-term (user context) memory
   - When to store vs retrieve

4. **AWS Services**
   - Bedrock Agents setup
   - Lambda functions
   - DynamoDB operations
   - EventBridge automation
   - S3 storage

5. **Integration Patterns**
   - External API integration (Garmin)
   - Data transformation pipelines
   - Error handling and retries

---

## 📦 Simplified Free Tier Implementation

### Phase 0: Setup & Prerequisites (Day 1)

**Goals:**
- Set up AWS account with free tier
- Install necessary tools
- Understand free tier limits

**Tasks:**

1. **AWS Account Setup**
   ```bash
   # Create AWS account (if you don't have one)
   # Enable free tier tracking in Billing Console
   # Set up billing alerts for $5, $10, $20
   ```

2. **Request Bedrock Model Access**
   - Go to AWS Console → Bedrock → Model access
   - Request access to:
     - ✅ Claude 3 Haiku (cheapest!)
     - ✅ Titan Embeddings G1 - Text
   - Wait for approval (usually instant)

3. **Install Tools**
   ```bash
   # Install AWS CLI
   pip install awscli
   aws configure

   # Install Python dependencies
   pip install boto3 garminconnect
   ```

4. **Set Up Free Tier Tracking**
   - Enable AWS Budgets (free for first 2 budgets)
   - Set budget: $10/month with alerts
   - Enable Cost Explorer

**Success Criteria:**
- ✅ AWS account active with free tier
- ✅ Bedrock models approved
- ✅ Billing alerts configured
- ✅ CLI tools installed

---

### Phase 1: Garmin Data Pipeline (Days 2-3)

**Goal:** Get your real health data into AWS (free!)

#### Step 1.1: DynamoDB Tables (Free Tier)

```bash
# Create Activities table
aws dynamodb create-table \
  --table-name HealthInsights-Activities \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --tags Key=Project,Value=HealthInsights

# Create SleepData table
aws dynamodb create-table \
  --table-name HealthInsights-SleepData \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=date,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
    AttributeName=date,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Create UserMemory table
aws dynamodb create-table \
  --table-name HealthInsights-UserMemory \
  --attribute-definitions \
    AttributeName=userId,AttributeType=S \
    AttributeName=memoryKey,AttributeType=S \
  --key-schema \
    AttributeName=userId,KeyType=HASH \
    AttributeName=memoryKey,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

**Why PAY_PER_REQUEST?**
- For low usage (single user), it's effectively free
- Free tier: 25 RCU/WCU covers ~2.5M requests/month
- Simpler than provisioned capacity

#### Step 1.2: Store Garmin Credentials

```bash
# Store credentials in Secrets Manager
aws secretsmanager create-secret \
  --name health-insights/garmin \
  --description "Garmin Connect credentials" \
  --secret-string '{"email":"your@email.com","password":"yourpassword"}'

# Cost: $0.40/month (unavoidable but minimal)
```

#### Step 1.3: Create Garmin Fetcher Lambda

**File:** `lambda/garmin_fetcher/lambda_function.py`

```python
import json
import boto3
import os
from datetime import datetime, timedelta
from garminconnect import Garmin
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secretsmanager = boto3.client('secretsmanager')
activities_table = dynamodb.Table('HealthInsights-Activities')
sleep_table = dynamodb.Table('HealthInsights-SleepData')

USER_ID = "personal"  # Single user - you!

def lambda_handler(event, context):
    """
    Fetch data from Garmin Connect and store in DynamoDB
    Triggered by EventBridge every hour
    """

    try:
        # Get Garmin credentials
        secret = secretsmanager.get_secret_value(SecretId='health-insights/garmin')
        creds = json.loads(secret['SecretString'])

        # Initialize Garmin client
        client = Garmin(creds['email'], creds['password'])
        client.login()

        # Fetch recent activities (last 7 days)
        activities = client.get_activities(0, 20)

        activities_stored = 0
        for activity in activities:
            activity_type = activity['activityType']['typeKey']

            # Only process swimming and running
            if activity_type in ['lap_swimming', 'open_water_swimming', 'running', 'trail_running']:
                store_activity(activity, client)
                activities_stored += 1

        # Fetch sleep data (yesterday)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            sleep_data = client.get_sleep_data(yesterday)
            store_sleep_data(yesterday, sleep_data)
        except Exception as e:
            print(f"No sleep data for {yesterday}: {e}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Garmin sync complete',
                'activitiesStored': activities_stored
            })
        }

    except Exception as e:
        print(f"Error syncing Garmin data: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def store_activity(activity, client):
    """Store activity in DynamoDB"""

    activity_id = str(activity['activityId'])
    activity_type = activity['activityType']['typeKey']
    timestamp = activity['startTimeLocal']

    # Check if already stored
    existing = activities_table.get_item(
        Key={'userId': USER_ID, 'timestamp': timestamp}
    )
    if 'Item' in existing:
        print(f"Activity {activity_id} already stored")
        return

    # Basic metrics
    item = {
        'userId': USER_ID,
        'timestamp': timestamp,
        'activityId': activity_id,
        'activityType': 'swimming' if 'swimming' in activity_type else 'running',
        'duration': Decimal(str(activity.get('duration', 0))),
        'distance': Decimal(str(activity.get('distance', 0))),
        'calories': Decimal(str(activity.get('calories', 0)))
    }

    # Add activity-specific metrics
    if 'swimming' in activity_type:
        item['metrics'] = {
            'strokes': Decimal(str(activity.get('strokes', 0))),
            'avgStrokeDistance': Decimal(str(activity.get('avgStrokeDistance', 0))),
            'poolLength': Decimal(str(activity.get('poolLength', 25)))
        }
    elif 'running' in activity_type:
        item['metrics'] = {
            'avgHeartRate': Decimal(str(activity.get('avgHr', 0))),
            'maxHeartRate': Decimal(str(activity.get('maxHr', 0))),
            'avgPace': Decimal(str(activity.get('avgSpeed', 0))),
            'elevationGain': Decimal(str(activity.get('elevationGain', 0)))
        }

    activities_table.put_item(Item=item)
    print(f"Stored activity {activity_id}")

def store_sleep_data(date, sleep_data):
    """Store sleep data in DynamoDB"""

    if not sleep_data:
        return

    item = {
        'userId': USER_ID,
        'date': date,
        'totalSleep': Decimal(str(sleep_data.get('dailySleepDTO', {}).get('sleepTimeSeconds', 0))),
        'deepSleep': Decimal(str(sleep_data.get('dailySleepDTO', {}).get('deepSleepSeconds', 0))),
        'lightSleep': Decimal(str(sleep_data.get('dailySleepDTO', {}).get('lightSleepSeconds', 0))),
        'remSleep': Decimal(str(sleep_data.get('dailySleepDTO', {}).get('remSleepSeconds', 0))),
        'awakeTime': Decimal(str(sleep_data.get('dailySleepDTO', {}).get('awakeSleepSeconds', 0))),
        'sleepScore': Decimal(str(sleep_data.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value', 0)))
    }

    sleep_table.put_item(Item=item)
    print(f"Stored sleep data for {date}")
```

**Deploy Lambda:**

```bash
# Create deployment package
cd lambda/garmin_fetcher
pip install garminconnect -t .
zip -r function.zip .

# Create IAM role for Lambda
aws iam create-role \
  --role-name HealthInsightsLambdaRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies (DynamoDB, Secrets Manager, CloudWatch Logs)
aws iam attach-role-policy \
  --role-name HealthInsightsLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name HealthInsightsLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

aws iam attach-role-policy \
  --role-name HealthInsightsLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

# Create Lambda function
aws lambda create-function \
  --function-name GarminDataFetcher \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/HealthInsightsLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 60 \
  --memory-size 256

# Test it manually first
aws lambda invoke \
  --function-name GarminDataFetcher \
  --payload '{}' \
  response.json

cat response.json
```

#### Step 1.4: Schedule with EventBridge (Free)

```bash
# Create EventBridge rule to run every hour
aws events put-rule \
  --name GarminHourlySync \
  --schedule-expression "rate(1 hour)" \
  --description "Sync Garmin data every hour"

# Add Lambda as target
aws events put-targets \
  --rule GarminHourlySync \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:GarminDataFetcher"

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
  --function-name GarminDataFetcher \
  --statement-id EventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/GarminHourlySync
```

**Test:**

```bash
# Check DynamoDB for data
aws dynamodb scan --table-name HealthInsights-Activities --limit 5

# Check CloudWatch logs
aws logs tail /aws/lambda/GarminDataFetcher --follow
```

**Success Criteria:**
- ✅ Lambda fetches Garmin data successfully
- ✅ Data appears in DynamoDB tables
- ✅ EventBridge triggers Lambda every hour
- ✅ Cost: $0 (within free tier)

---

### Phase 2: Bedrock Agent with Action Groups (Days 4-5)

**Goal:** Create the AI agent that can answer questions about your data

#### Step 2.1: Create Action Handler Lambda

**File:** `lambda/action_handler/lambda_function.py`

```python
import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
activities_table = dynamodb.Table('HealthInsights-Activities')
sleep_table = dynamodb.Table('HealthInsights-SleepData')
memory_table = dynamodb.Table('HealthInsights-UserMemory')

USER_ID = "personal"

def lambda_handler(event, context):
    """
    Handle Bedrock Agent action group calls
    """

    print(f"Event: {json.dumps(event)}")

    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    parameters = event.get('parameters', [])

    # Convert parameters list to dict
    params = {p['name']: p['value'] for p in parameters}

    # Route to appropriate handler
    if api_path == '/activities/recent':
        result = get_recent_activities(params)
    elif api_path == '/sleep/recent':
        result = get_recent_sleep(params)
    elif api_path == '/memory/context':
        result = get_user_context()
    elif api_path == '/memory/save':
        result = save_memory(params)
    else:
        result = {'error': f'Unknown API path: {api_path}'}

    # Format response for Bedrock Agent
    response = {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': event.get('httpMethod', 'GET'),
            'httpStatusCode': 200,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(result, default=decimal_default)
                }
            }
        }
    }

    return response

def get_recent_activities(params):
    """Get recent swimming and running activities"""

    days = int(params.get('days', 7))
    activity_type = params.get('type', 'all')  # 'swimming', 'running', or 'all'

    # Query last N days
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    response = activities_table.query(
        KeyConditionExpression='userId = :uid AND #ts > :cutoff',
        ExpressionAttributeNames={'#ts': 'timestamp'},
        ExpressionAttributeValues={
            ':uid': USER_ID,
            ':cutoff': cutoff
        },
        ScanIndexForward=False
    )

    activities = response.get('Items', [])

    # Filter by type if specified
    if activity_type != 'all':
        activities = [a for a in activities if a['activityType'] == activity_type]

    # Calculate summary
    summary = calculate_activity_summary(activities, activity_type)

    return {
        'activities': activities[:10],  # Return max 10 for token efficiency
        'summary': summary,
        'totalCount': len(activities)
    }

def get_recent_sleep(params):
    """Get recent sleep data"""

    days = int(params.get('days', 7))

    # Get last N days of sleep
    sleep_data = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')
        response = sleep_table.get_item(Key={'userId': USER_ID, 'date': date})
        if 'Item' in response:
            sleep_data.append(response['Item'])

    # Calculate averages
    if sleep_data:
        avg_total = sum(s['totalSleep'] for s in sleep_data) / len(sleep_data)
        avg_score = sum(s.get('sleepScore', 0) for s in sleep_data) / len(sleep_data)
        avg_deep = sum(s['deepSleep'] for s in sleep_data) / len(sleep_data)
    else:
        avg_total = avg_score = avg_deep = 0

    return {
        'sleepData': sleep_data,
        'summary': {
            'avgTotalSleepHours': float(avg_total) / 3600,
            'avgSleepScore': float(avg_score),
            'avgDeepSleepHours': float(avg_deep) / 3600,
            'nightsTracked': len(sleep_data)
        }
    }

def get_user_context():
    """Get user goals and preferences from memory"""

    # Get all memory items
    response = memory_table.query(
        KeyConditionExpression='userId = :uid',
        ExpressionAttributeValues={':uid': USER_ID}
    )

    memory_items = response.get('Items', [])

    # Organize by type
    context = {
        'goals': {},
        'preferences': {},
        'insights': []
    }

    for item in memory_items:
        mem_key = item['memoryKey']
        if mem_key.startswith('goal:'):
            context['goals'][mem_key.replace('goal:', '')] = item['value']
        elif mem_key.startswith('pref:'):
            context['preferences'][mem_key.replace('pref:', '')] = item['value']
        elif mem_key.startswith('insight:'):
            context['insights'].append(item)

    return context

def save_memory(params):
    """Save a memory item"""

    mem_type = params.get('type', 'insight')  # 'goal', 'preference', 'insight'
    key = params.get('key', '')
    value = params.get('value', '')

    memory_key = f"{mem_type}:{key}"

    memory_table.put_item(Item={
        'userId': USER_ID,
        'memoryKey': memory_key,
        'value': value,
        'timestamp': datetime.now().isoformat()
    })

    return {'success': True, 'memoryKey': memory_key}

def calculate_activity_summary(activities, activity_type):
    """Calculate summary statistics"""

    if not activities:
        return {}

    total_distance = sum(a.get('distance', 0) for a in activities)
    total_duration = sum(a.get('duration', 0) for a in activities)

    summary = {
        'totalDistance': float(total_distance),
        'totalDuration': float(total_duration),
        'sessionCount': len(activities),
        'avgDistance': float(total_distance / len(activities)),
        'avgDuration': float(total_duration / len(activities))
    }

    if activity_type == 'swimming':
        activities_with_strokes = [a for a in activities if 'metrics' in a and 'strokes' in a['metrics']]
        if activities_with_strokes:
            avg_strokes = sum(a['metrics']['strokes'] for a in activities_with_strokes) / len(activities_with_strokes)
            summary['avgStrokes'] = float(avg_strokes)

    elif activity_type == 'running':
        activities_with_hr = [a for a in activities if 'metrics' in a and 'avgHeartRate' in a['metrics']]
        if activities_with_hr:
            avg_hr = sum(a['metrics']['avgHeartRate'] for a in activities_with_hr) / len(activities_with_hr)
            summary['avgHeartRate'] = float(avg_hr)

    return summary

def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
```

**Deploy:**

```bash
cd lambda/action_handler
zip -r function.zip lambda_function.py

aws lambda create-function \
  --function-name HealthInsightsActionHandler \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/HealthInsightsLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256
```

#### Step 2.2: Create OpenAPI Schema for Action Group

**File:** `bedrock/action_group_schema.json`

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Health Insights API",
    "version": "1.0.0",
    "description": "API for retrieving health and fitness data"
  },
  "paths": {
    "/activities/recent": {
      "get": {
        "summary": "Get recent activities (swimming or running)",
        "description": "Retrieves recent swimming and running activities with summary statistics",
        "operationId": "getRecentActivities",
        "parameters": [
          {
            "name": "days",
            "in": "query",
            "description": "Number of days to look back (default: 7)",
            "required": false,
            "schema": {
              "type": "integer",
              "default": 7
            }
          },
          {
            "name": "type",
            "in": "query",
            "description": "Activity type: 'swimming', 'running', or 'all'",
            "required": false,
            "schema": {
              "type": "string",
              "enum": ["swimming", "running", "all"],
              "default": "all"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "List of activities with summary",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "activities": {
                      "type": "array",
                      "items": {
                        "type": "object"
                      }
                    },
                    "summary": {
                      "type": "object"
                    },
                    "totalCount": {
                      "type": "integer"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/sleep/recent": {
      "get": {
        "summary": "Get recent sleep data",
        "description": "Retrieves recent sleep metrics with averages",
        "operationId": "getRecentSleep",
        "parameters": [
          {
            "name": "days",
            "in": "query",
            "description": "Number of days to look back (default: 7)",
            "required": false,
            "schema": {
              "type": "integer",
              "default": 7
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Sleep data with summary",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "sleepData": {
                      "type": "array"
                    },
                    "summary": {
                      "type": "object"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/memory/context": {
      "get": {
        "summary": "Get user context and goals",
        "description": "Retrieves user's goals, preferences, and recent insights from memory",
        "operationId": "getUserContext",
        "responses": {
          "200": {
            "description": "User context",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "goals": {
                      "type": "object"
                    },
                    "preferences": {
                      "type": "object"
                    },
                    "insights": {
                      "type": "array"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/memory/save": {
      "post": {
        "summary": "Save a memory item",
        "description": "Saves a goal, preference, or insight to user memory",
        "operationId": "saveMemory",
        "parameters": [
          {
            "name": "type",
            "in": "query",
            "description": "Memory type: 'goal', 'preference', or 'insight'",
            "required": true,
            "schema": {
              "type": "string",
              "enum": ["goal", "preference", "insight"]
            }
          },
          {
            "name": "key",
            "in": "query",
            "description": "Memory key (e.g., 'swimming_target', 'pool_length')",
            "required": true,
            "schema": {
              "type": "string"
            }
          },
          {
            "name": "value",
            "in": "query",
            "description": "Memory value",
            "required": true,
            "schema": {
              "type": "string"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Memory saved successfully"
          }
        }
      }
    }
  }
}
```

#### Step 2.3: Create Bedrock Agent (AWS Console)

**Using AWS Console (Easiest for Learning):**

1. **Go to Bedrock Console** → Agents → Create Agent

2. **Agent Details:**
   - Agent name: `HealthInsightsCoach`
   - Description: `Personal health coaching agent for swimming, running, and sleep`
   - User input: Enable

3. **Agent Instructions:**
   ```
   You are a personal health and fitness coach specializing in:
   - Swimming: technique, training, and performance analysis
   - Running: training plans for 10-20KM distances, pacing strategies
   - Sleep: recovery optimization and sleep quality analysis

   You have access to the user's real activity data from Garmin Connect.

   When answering questions:
   1. Always retrieve recent data using your tools first
   2. Provide specific, data-driven insights based on actual metrics
   3. Be encouraging and supportive
   4. Give actionable advice, not just observations
   5. Remember user's goals and reference them in your advice

   If you don't have data yet, ask the user to ensure their Garmin device is synced.

   Keep responses concise but informative. You're a coach, not just a data reporter.
   ```

4. **Model Selection:**
   - Model: **Claude 3 Haiku** (12x cheaper than Sonnet!)
   - Temperature: 1.0 (default)
   - Top P: 0.999
   - Top K: 250

5. **Add Action Group:**
   - Name: `HealthDataTools`
   - Description: `Tools to retrieve activity, sleep, and memory data`
   - Action group type: Define with API schemas
   - Upload `action_group_schema.json`
   - Action group executor: Lambda function → `HealthInsightsActionHandler`

6. **Create Agent** → Wait for creation

7. **Create Alias:**
   - Alias name: `prod`
   - Description: `Production alias`

**Test in Console:**

Click "Test" button and try:
- "What were my swimming sessions this week?"
- "How is my sleep quality?"
- "Show me my running data"

#### Step 2.4: Grant Bedrock Permission to Invoke Lambda

```bash
aws lambda add-permission \
  --function-name HealthInsightsActionHandler \
  --statement-id AllowBedrockInvoke \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-arn arn:aws:bedrock:us-east-1:YOUR_ACCOUNT_ID:agent/YOUR_AGENT_ID
```

**Success Criteria:**
- ✅ Agent created successfully
- ✅ Agent can invoke action group Lambda
- ✅ Agent returns real data from DynamoDB
- ✅ Test queries work in console
- ✅ Cost: $0-2 for testing (Haiku is cheap!)

---

### Phase 3: Lightweight Knowledge Base (Days 6-7)

**Goal:** Add coaching knowledge without expensive OpenSearch

#### Option A: Bedrock Knowledge Base (Recommended for Learning)

**Why:** Even without OpenSearch, Bedrock KB can use S3 + embeddings for simple RAG

**Steps:**

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://health-insights-kb-YOUR-ACCOUNT-ID
   ```

2. **Prepare Coaching Documents:**

   Create simple markdown files:

   **`swimming-technique.md`:**
   ```markdown
   # Swimming Technique Guide

   ## Freestyle Technique

   ### Body Position
   - Keep body horizontal in water
   - Head neutral, looking at pool bottom
   - Hips near surface

   ### Stroke Mechanics
   - High elbow catch
   - Pull through to hips
   - Smooth recovery over water

   ### SWOLF Score
   SWOLF = Strokes + Time (for 25m/50m pool length)
   - Excellent: < 40
   - Good: 40-45
   - Average: 45-50
   - Needs improvement: > 50

   To improve SWOLF:
   1. Reduce stroke count (efficiency drills)
   2. Increase speed (interval training)
   3. Focus on glide and reach
   ```

   **`running-training.md`:**
   ```markdown
   # Running Training Guide

   ## 10K Training

   ### Training Phases
   1. Base building (4-6 weeks)
   2. Speed work (4-6 weeks)
   3. Race preparation (2-3 weeks)
   4. Taper (1 week)

   ### Weekly Structure
   - Easy runs: 3-4 per week (conversational pace)
   - Tempo run: 1 per week (comfortably hard)
   - Intervals: 1 per week (track or hill repeats)
   - Long run: 1 per week (60-90 minutes)
   - Rest: 1-2 days

   ### Half Marathon (20KM)
   Build from 10K base:
   - Increase long run gradually (10% per week)
   - Peak long run: 16-18KM
   - Focus on aerobic endurance
   - Practice race pace in training

   ### Pacing Strategy
   - First 5K: Start conservative (5-10s slower than goal pace)
   - Middle 5K: Settle into goal pace
   - Final 5K: Push if feeling good, maintain if struggling
   ```

   **`sleep-recovery.md`:**
   ```markdown
   # Sleep and Recovery Guide

   ## Sleep Metrics Explained

   ### Sleep Score (0-100)
   - 90-100: Excellent
   - 80-89: Good
   - 70-79: Fair
   - <70: Poor

   ### Sleep Stages

   **Deep Sleep:**
   - Physical recovery
   - Muscle repair
   - Immune system boost
   - Target: 15-25% of total sleep

   **REM Sleep:**
   - Mental recovery
   - Memory consolidation
   - Learning
   - Target: 20-25% of total sleep

   **Light Sleep:**
   - Transition stage
   - Still restorative
   - Target: 50-60% of total sleep

   ## Sleep Hygiene for Athletes

   1. **Consistency:** Same bedtime/wake time daily
   2. **Environment:** Cool (60-67°F), dark, quiet
   3. **Pre-bed routine:** Wind down 30-60 min before sleep
   4. **Avoid:**
      - Caffeine after 2 PM
      - Heavy meals before bed
      - Blue light (screens) 1 hour before sleep
      - Intense training within 3 hours of bedtime

   ## Recovery Indicators

   **Well Recovered:**
   - Sleep score > 80
   - Deep sleep > 1.5 hours
   - Wake up feeling refreshed
   - Resting heart rate normal

   **Need More Recovery:**
   - Sleep score < 70
   - Frequent awakenings
   - Low deep sleep
   - Elevated resting heart rate

   Action: Easy training day or rest
   ```

3. **Upload to S3:**
   ```bash
   aws s3 cp swimming-technique.md s3://health-insights-kb-YOUR-ACCOUNT-ID/
   aws s3 cp running-training.md s3://health-insights-kb-YOUR-ACCOUNT-ID/
   aws s3 cp sleep-recovery.md s3://health-insights-kb-YOUR-ACCOUNT-ID/
   ```

4. **Create Knowledge Base (AWS Console):**

   Go to Bedrock → Knowledge bases → Create knowledge base

   - Name: `HealthCoachingKB`
   - IAM role: Create new role
   - Data source: S3
   - S3 URI: `s3://health-insights-kb-YOUR-ACCOUNT-ID/`
   - Embedding model: **Titan Embeddings G1 - Text** (cheap!)
   - Vector database: **Amazon OpenSearch Serverless**
     - Unfortunately, this is required by Bedrock KB
     - Cost: ~$60/month for minimal usage
     - **ALTERNATIVE**: Skip KB for now, see Option B below

5. **Sync Data Source**

#### Option B: In-Memory Knowledge (FREE!)

**If you want to stay 100% free tier**, skip the knowledge base and embed knowledge directly in the agent instructions:

**Modified Agent Instructions:**

```
You are a personal health and fitness coach specializing in swimming, running, and sleep.

KNOWLEDGE BASE:

SWIMMING:
- SWOLF Score: Strokes + Time for 25m/50m. Excellent: <40, Good: 40-45, Average: 45-50
- Improve SWOLF by: reducing stroke count (efficiency drills), increasing speed (intervals), focusing on glide
- Freestyle technique: horizontal body, neutral head, high elbow catch, pull to hips

RUNNING:
- 10K Training: Base building (4-6 weeks), Speed work (4-6 weeks), Race prep (2-3 weeks), Taper (1 week)
- Weekly structure: 3-4 easy runs, 1 tempo, 1 intervals, 1 long run, 1-2 rest days
- Half Marathon: Build from 10K base, increase long run 10%/week, peak 16-18KM
- Pacing: Start 5-10s slower than goal, settle into pace, push final 5K if feeling good

SLEEP:
- Sleep score: 90-100 excellent, 80-89 good, 70-79 fair, <70 poor
- Deep sleep target: 15-25% (physical recovery)
- REM sleep target: 20-25% (mental recovery)
- Good recovery: score >80, deep sleep >1.5hrs, normal resting HR
- Need recovery: score <70, low deep sleep, elevated HR → easy day or rest

When answering questions:
1. Retrieve user's actual data first using your tools
2. Combine data with coaching knowledge above
3. Give specific, actionable advice
4. Be encouraging and supportive
```

**Pros:**
- **100% Free!**
- No knowledge base costs
- Faster responses (no KB retrieval)
- Simpler architecture

**Cons:**
- Limited knowledge (fits in prompt)
- Can't easily add more documents
- Less sophisticated RAG

**Recommendation for Learning:**
- Start with Option B (in-memory)
- Learn the agent basics for free
- Add knowledge base later when you understand the value

**Success Criteria:**
- ✅ Agent has coaching knowledge
- ✅ Can answer technique questions
- ✅ Combines knowledge with user data
- ✅ Cost: $0 (Option B) or $60/month (Option A)

---

### Phase 4: Simple CLI Interface (Day 8)

**Goal:** Chat with your agent from command line (free!)

**File:** `chat.py`

```python
#!/usr/bin/env python3
import boto3
import sys
import json
from datetime import datetime

# Initialize Bedrock Agent Runtime client
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# Your agent details (get from console)
AGENT_ID = "YOUR_AGENT_ID"  # e.g., "ABCDEFGH12"
AGENT_ALIAS_ID = "YOUR_ALIAS_ID"  # e.g., "TSTALIASID"

def chat():
    """
    Simple CLI chat interface
    """

    print("🏊 Health Insights Coach 🏃")
    print("=" * 50)
    print("Ask me about your swimming, running, or sleep!")
    print("Type 'quit' to exit\n")

    session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Keep training! See you next time!")
                break

            # Call Bedrock Agent
            print("\n🤖 Coach: ", end='', flush=True)

            response = bedrock_agent.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=session_id,
                inputText=user_input
            )

            # Stream the response
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        text = chunk['bytes'].decode('utf-8')
                        print(text, end='', flush=True)

            print()  # New line after response

        except KeyboardInterrupt:
            print("\n\n👋 Keep training! See you next time!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Make sure your AWS credentials are configured and agent ID is correct.")

if __name__ == "__main__":
    chat()
```

**Usage:**

```bash
# Make executable
chmod +x chat.py

# Update AGENT_ID and AGENT_ALIAS_ID in the script

# Run
./chat.py
```

**Example Session:**

```
🏊 Health Insights Coach 🏃
==================================================
Ask me about your swimming, running, or sleep!
Type 'quit' to exit

You: What were my swimming sessions this week?

🤖 Coach: Let me check your recent swimming activities...

Based on your Garmin data, you had 3 swimming sessions this week:

1. Monday: 2000m in 45 minutes (750 strokes)
2. Wednesday: 1500m in 35 minutes (590 strokes)
3. Friday: 2500m in 55 minutes (920 strokes)

Your average SWOLF score across these sessions is around 43, which is in the "good" range.
I notice your stroke count is consistent around 360-370 strokes per 1000m, which shows
good efficiency.

To improve further, I recommend:
- Incorporate some stroke count drills to reduce strokes per length
- Focus on your glide phase to maximize distance per stroke
- Try some tempo trainer work to maintain efficiency at higher speeds

Great consistency this week! 💪

You: How's my sleep been?

🤖 Coach: Let me pull up your recent sleep data...

Over the past 7 nights, your sleep has been quite good:
- Average total sleep: 7.3 hours
- Average sleep score: 82 (Good range)
- Average deep sleep: 1.8 hours (excellent!)

However, I notice your sleep score dropped to 68 on Wednesday night, right after your
hard running session Tuesday evening. This is common - intense evening workouts can
disrupt sleep quality.

Recommendations:
- Try to schedule intense workouts earlier in the day when possible
- If evening workouts are necessary, allow 3-4 hours before bedtime
- Consider light stretching or yoga before bed after hard training days

Your deep sleep percentage is excellent at 25%, which means you're getting great physical
recovery. Keep up the good work! 😴

You: quit

👋 Keep training! See you next time!
```

**Success Criteria:**
- ✅ Can chat with agent from CLI
- ✅ Agent retrieves real data
- ✅ Responses are helpful and personalized
- ✅ Cost: $0 for CLI (uses existing agent)

---

### Phase 5: Set User Goals (Day 9)

**Goal:** Teach agent to remember your goals

**Usage:**

```bash
./chat.py
```

**Example:**

```
You: I want to improve my 100m freestyle time to under 1:30

🤖 Coach: That's a great goal! Let me save that for you...

I've recorded your swimming goal: improve 100m freestyle to under 1:30.

Based on your recent swimming data, you're currently averaging around 1:48/100m pace
in your workouts. To reach your goal of 1:30/100m, you'll need to improve by about
18 seconds.

This is definitely achievable! Here's what I recommend:

1. **Technique work (2x per week):**
   - Focus on reducing drag (body position drills)
   - High elbow catch practice
   - Improve your turns and push-offs

2. **Speed work (1x per week):**
   - 8-10 x 50m at goal pace (1:15/50m)
   - Rest 30-45 seconds between reps
   - Focus on maintaining form at speed

3. **Test sets (every 2 weeks):**
   - Time yourself on 100m to track progress

Would you like me to create a detailed training plan?

You: Yes, create a training plan

🤖 Coach: I'll create a plan for you and save it to memory...

[Agent uses saveMemory tool to store the plan]

I've created an 8-week training plan to help you reach your 1:30/100m freestyle goal...
[Detailed plan follows]
```

**Testing Memory:**

Exit and restart chat.py with a new session:

```
You: What are my swimming goals?

🤖 Coach: Let me check your goals...

Your swimming goal is to improve your 100m freestyle time to under 1:30.
You're currently working on an 8-week training plan I created for you.

Would you like a progress update on how you're doing toward this goal?
```

**Success Criteria:**
- ✅ Agent can save goals to memory
- ✅ Agent remembers goals across sessions
- ✅ Agent references goals in coaching advice
- ✅ Cost: $0 (DynamoDB free tier)

---

## 📚 Learning Checkpoints

After completing this plan, you should understand:

### ✅ AI Agent Concepts
- [x] How agents orchestrate multiple tools
- [x] When agents call tools vs use knowledge
- [x] How to engineer agent instructions
- [x] Session vs persistent memory

### ✅ AWS Services
- [x] Bedrock Agents architecture
- [x] Lambda function development
- [x] DynamoDB data modeling
- [x] EventBridge scheduling
- [x] IAM roles and permissions

### ✅ RAG (Retrieval Augmented Generation)
- [x] What RAG is and why it's useful
- [x] How embeddings work (conceptually)
- [x] Trade-offs: in-memory vs vector DB
- [x] When to use RAG vs fine-tuning

### ✅ Integration Patterns
- [x] External API integration (Garmin)
- [x] Data transformation pipelines
- [x] Error handling and retries
- [x] Cron-style automation

---

## 🎓 Next Steps for Learning

### Option 1: Add Web UI
Build a simple web interface:
- HTML/JS chat interface
- Deploy to S3 static hosting (free tier)
- Use API Gateway + Lambda (free tier first 12 months)

### Option 2: Add Knowledge Base
If you want to learn vector search:
- Add Bedrock Knowledge Base (~$60/month)
- Understand embeddings and similarity search
- Compare results with in-memory knowledge

### Option 3: Add More Features
Enhance the agent:
- Training plan generation
- Progress tracking and charts
- Weekly summary emails (SES free tier)
- Proactive insights

### Option 4: Try Other Agent Frameworks
Compare approaches:
- Build same agent with LangChain
- Build with AWS AgentCore (lower level)
- Build with Strands SDK

---

## 💰 Final Cost Summary

### Monthly Costs (Single User, Learning Usage)

| Service | Usage | Cost |
|---------|-------|------|
| **DynamoDB** | 3 tables, minimal writes | **$0** (free tier) |
| **Lambda** | ~2K invocations/month | **$0** (free tier) |
| **S3** | <1GB storage | **$0** (free tier first 12 months) |
| **EventBridge** | 720 events/month (hourly) | **$0** (free tier) |
| **Bedrock Claude Haiku** | ~50K tokens/month | **$0.01** (minimal) |
| **Bedrock Titan Embeddings** | Minimal usage | **$0.01** (if using KB) |
| **Secrets Manager** | 1 secret | **$0.40** |
| **CloudWatch** | Basic logs | **$0** (free tier) |
| **Knowledge Base (optional)** | OpenSearch Serverless | **$60** (skip for free version) |
| **TOTAL (without KB)** | | **$0.42/month** |
| **TOTAL (with KB)** | | **$60.42/month** |

### Free Tier Limits to Monitor

✅ **DynamoDB:** 25GB storage, 25 RCU/WCU (plenty for single user)
✅ **Lambda:** 1M requests, 400K GB-seconds (plenty)
✅ **S3:** 5GB storage first 12 months (plenty)
✅ **EventBridge:** 14M events/month (more than enough)
✅ **CloudWatch:** 5GB logs (plenty)

### Cost Optimization Tips

1. **Use Haiku over Sonnet:** 12x cheaper ($0.25 vs $3 per MTok)
2. **Skip Knowledge Base initially:** Save $60/month
3. **Set billing alerts:** $5, $10, $20 thresholds
4. **Monitor token usage:** Keep prompts concise
5. **Use PAY_PER_REQUEST for DynamoDB:** Free tier covers it

---

## 🚀 Quick Start Guide

### Day 1: Setup
```bash
# 1. Create AWS account, request Bedrock access
# 2. Set billing alert for $10
# 3. Install tools: pip install boto3 garminconnect awscli
# 4. Configure: aws configure
```

### Day 2: Garmin Pipeline
```bash
# 1. Create DynamoDB tables
# 2. Store Garmin credentials in Secrets Manager
# 3. Deploy GarminDataFetcher Lambda
# 4. Test manually, then schedule with EventBridge
# 5. Verify data in DynamoDB
```

### Day 3-4: Bedrock Agent
```bash
# 1. Deploy ActionHandler Lambda
# 2. Create OpenAPI schema
# 3. Create Bedrock Agent in console
# 4. Add action group
# 5. Create alias and test
```

### Day 5: Add Knowledge
```bash
# Option A: Skip KB, use in-memory (FREE)
# Option B: Create S3 KB ($60/month)
```

### Day 6: CLI Interface
```bash
# 1. Create chat.py
# 2. Update agent/alias IDs
# 3. Test chatting with your agent!
```

### Day 7: Set Goals & Memory
```bash
# 1. Chat with agent to set goals
# 2. Verify goals saved in DynamoDB
# 3. Start new session, verify agent remembers
```

---

## 📖 Resources for Learning

### AWS Documentation
- [Bedrock Agents User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [DynamoDB Getting Started](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStartedDynamoDB.html)
- [Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)

### Free Learning Resources
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Garmin Connect Python Library](https://github.com/cyberjunky/python-garminconnect)
- [AWS Samples - Bedrock Agents](https://github.com/aws-samples/amazon-bedrock-samples)

### Your Repository Resources
- `/home/user/MyFirstRepo/AWS_BEDROCK_AGENT_PLAN.md` - Original detailed plan
- `/home/user/MyFirstRepo/Learning/lessons/` - AI agent lessons
- `/home/user/MyFirstRepo/01-personal/aws-ai-agent/` - Reference patterns

---

## 🎯 Success Criteria

By the end of this plan, you should have:

- ✅ Working Garmin → AWS data pipeline
- ✅ Bedrock Agent that answers questions about your health data
- ✅ Memory system that remembers your goals
- ✅ CLI interface to chat with your agent
- ✅ Understanding of AI agent architecture
- ✅ Cost under $5/month (or $0.42 without KB!)

**Most importantly:** You'll understand how AI agents work and can build more complex agents in the future!

---

**Last Updated:** 2026-01-16
**Version:** 2.0 - Free Tier Optimized
**Status:** Ready to implement!
**Estimated Time:** 7-9 days at your own pace
**Cost:** $0.42-5/month (or $60 with Knowledge Base)
