# Garmin Health Backend — API Reference

AWS Lambda + API Gateway endpoints for the Garmin health ingestion pipeline.

**Base URL**: [Retrieved from CloudFormation outputs or API Gateway console]  
**Status**: Alpha  
**Authentication**: API Key (x-api-key header)

---

## Overview

The Garmin Health backend provides three main capabilities:

1. **OAuth Flow** — Authenticate with Garmin API
2. **Activity Ingestion** — Webhook receiver for new Garmin activities
3. **Data Query** — Retrieve activities from DynamoDB

---

## Authentication

### API Key

All requests require an API key in the header:

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://api-gateway.example.com/dev/activities
```

**How to get an API key:**
1. Deploy infrastructure: `bash scripts/deploy.sh`
2. Check CloudFormation outputs for `ApiKeyId`
3. Retrieve key: `aws apigateway get-api-key --id <ApiKeyId> --include-value`

---

## Endpoints

### OAuth Flow

#### Start OAuth

Initiate Garmin OAuth2 authentication.

**Endpoint**
```
GET /oauth/authorize
```

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `redirect_uri` | string | Yes | Where to redirect after auth |

**Response**
```json
{
  "authorize_url": "https://connect.garmin.com/oauthConfirm?...",
  "state": "random_state_string"
}
```

**Example**
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://api.example.com/dev/oauth/authorize?redirect_uri=https://yourapp.com/callback"
```

---

#### OAuth Callback

Handle Garmin OAuth callback and exchange code for token.

**Endpoint**
```
POST /oauth/callback
```

**Request Body**
```json
{
  "code": "garmin_auth_code",
  "state": "random_state_string"
}
```

**Response** (200 OK)
```json
{
  "access_token": "token_value",
  "expires_in": 3600,
  "refresh_token": "refresh_token_value"
}
```

**Status Codes**
| Code | Meaning |
|------|---------|
| 200 | OAuth successful, tokens returned |
| 400 | Invalid code or state |
| 401 | Unauthorized |

---

### Activity Ingestion

#### Webhook Receiver

Receive new activities from Garmin webhook.

**Endpoint**
```
POST /webhook/activity
```

**Request Body** (Garmin format)
```json
{
  "userId": 12345,
  "activityId": 67890,
  "uploadedTime": "2026-04-13T16:45:00Z",
  "activityType": "running",
  "startTime": "2026-04-13T08:30:00Z",
  "duration": 3600,
  "distance": 10500,
  "pace": "5:42 /km",
  "calories": 850
}
```

**Response** (202 Accepted)
```json
{
  "status": "processing",
  "activityId": "67890",
  "message": "Activity queued for processing"
}
```

**Status Codes**
| Code | Meaning |
|------|---------|
| 202 | Accepted (async processing) |
| 400 | Invalid webhook data |
| 401 | Unauthorized |

**Headers**
```
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

**Example**
```bash
curl -X POST \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @webhook_payload.json \
  https://api.example.com/dev/webhook/activity
```

---

### Data Query

#### List Activities

Retrieve activities from DynamoDB.

**Endpoint**
```
GET /activities
```

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Items per page (default: 20, max: 100) |
| `date_from` | string | No | ISO date (e.g., 2026-01-01) |
| `date_to` | string | No | ISO date (e.g., 2026-04-13) |
| `activity_type` | string | No | Filter by type (running, swimming, etc.) |

**Response**
```json
{
  "activities": [
    {
      "id": "activity_123",
      "date": "2026-04-13",
      "type": "running",
      "distance": 10500,
      "duration_seconds": 3600,
      "pace_per_km": "5:42",
      "calories": 850,
      "heart_rate_avg": 165,
      "heart_rate_max": 185,
      "timestamp": "2026-04-13T16:45:00Z"
    }
  ],
  "count": 1,
  "last_evaluated_key": null
}
```

**Example**
```bash
# Get last 30 days of running
curl -H "x-api-key: YOUR_API_KEY" \
  "https://api.example.com/dev/activities?activity_type=running&limit=50&date_from=2026-03-14"
```

---

#### Get Single Activity

Retrieve details for a specific activity.

**Endpoint**
```
GET /activities/{activity_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| `activity_id` | string | Unique activity ID from Garmin |

**Response**
```json
{
  "id": "activity_123",
  "date": "2026-04-13",
  "type": "running",
  "distance": 10500,
  "duration_seconds": 3600,
  "pace_per_km": "5:42",
  "calories": 850,
  "heart_rate_avg": 165,
  "heart_rate_max": 185,
  "elevation_gain": 150,
  "timestamp": "2026-04-13T16:45:00Z",
  "splits": [
    {
      "distance": 1000,
      "pace": "5:35",
      "heart_rate": 160
    }
  ]
}
```

**Example**
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://api.example.com/dev/activities/activity_123"
```

---

#### Get Sleep Data

Retrieve sleep records.

**Endpoint**
```
GET /sleep
```

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Days to retrieve (default: 30) |
| `date_from` | string | No | ISO date |
| `date_to` | string | No | ISO date |

**Response**
```json
{
  "sleep_records": [
    {
      "date": "2026-04-12",
      "duration_seconds": 28800,
      "quality_score": 85,
      "rem_seconds": 5400,
      "deep_sleep_seconds": 7200,
      "light_sleep_seconds": 15600,
      "awake_seconds": 600,
      "timestamp": "2026-04-13T07:00:00Z"
    }
  ],
  "count": 30
}
```

---

#### Get Wellness Data

Retrieve daily wellness metrics.

**Endpoint**
```
GET /wellness
```

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Days to retrieve (default: 30) |
| `date_from` | string | No | ISO date |

**Response**
```json
{
  "wellness_records": [
    {
      "date": "2026-04-13",
      "resting_heart_rate": 55,
      "heart_rate_variability": 45,
      "stress_level": 30,
      "steps": 8500,
      "body_battery": 82,
      "timestamp": "2026-04-13T00:00:00Z"
    }
  ],
  "count": 30
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request",
    "details": "Missing required parameter: date_from"
  }
}
```

**Common Error Codes**
| Code | HTTP | Meaning |
|------|------|---------|
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `INVALID_REQUEST` | 400 | Malformed request |
| `NOT_FOUND` | 404 | Activity not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Lambda Functions

### fetch-activity

Invoked by Garmin webhook. Fetches detailed activity data and stores in DynamoDB.

**Trigger**: API Gateway (POST /webhook/activity)

**Environment Variables**
- `GARMIN_API_KEY` — Garmin API credentials
- `DYNAMODB_TABLE` — Activity table name
- `ENVIRONMENT` — dev/prod

**Logs**: CloudWatch `/aws/lambda/fetch-activity`

---

### oauth-handler

Manages Garmin OAuth2 flow.

**Trigger**: API Gateway (GET /oauth/authorize, POST /oauth/callback)

**Stores**: Tokens in DynamoDB with TTL

---

### backfill-activities

Historical data import (manual invocation).

```bash
aws lambda invoke \
  --function-name garmin-backfill-activities \
  --payload '{"start_date":"2026-01-01","end_date":"2026-04-13"}' \
  response.json
```

---

## Rate Limits

- **Requests per minute**: 30
- **Request body size**: 5MB max
- **DynamoDB writes**: Throttled by provisioned capacity

**Headers**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1713024300
```

---

## Monitoring

### CloudWatch Dashboards

```bash
# View Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=fetch-activity \
  --start-time 2026-04-12T00:00:00Z \
  --end-time 2026-04-13T23:59:59Z \
  --period 3600 \
  --statistics Average,Maximum
```

### Error Tracking

```bash
# View Lambda errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/fetch-activity \
  --filter-pattern "ERROR" \
  --start-time 1713052800000
```

---

## Testing

### Integration Tests

```bash
cd tests
python -m pytest test_api_endpoints.py -v

# Test specific endpoint
pytest tests/test_api_endpoints.py::test_list_activities -v
```

### Manual Testing

```bash
# Test webhook
curl -X POST \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": 12345,
    "activityId": 67890,
    "uploadedTime": "2026-04-13T16:45:00Z",
    "activityType": "running",
    "distance": 10500
  }' \
  https://api.example.com/dev/webhook/activity

# Query activities
curl -H "x-api-key: YOUR_API_KEY" \
  "https://api.example.com/dev/activities?activity_type=running"
```

---

## Deployment

Infrastructure defined in `terraform/`:

```bash
cd terraform
terraform init
terraform plan -var-file="../config/terraform.tfvars"
terraform apply -var-file="../config/terraform.tfvars"
```

Outputs include:
- API Gateway endpoint URL
- API Key ID
- DynamoDB table name
- Lambda function ARNs

---

## Support

- **Issue tracker**: Check `TODO.md`
- **Logs**: CloudWatch or `aws logs tail`
- **Status**: See `CLAUDE.md` for project status

---

**Last updated**: 2026-04-13
