# Garmin Connect AI Integration

Automatically analyze Garmin fitness activities using AWS Bedrock AI. This integration receives activity data from Garmin Connect webhooks, fetches detailed metrics, and provides AI-powered fitness insights and recommendations.

## 🎯 Features

- **Automatic Activity Detection**: Receives webhooks when new activities are uploaded to Garmin Connect
- **Comprehensive Data Fetching**: Retrieves detailed activity metrics via Garmin Health API
- **AI-Powered Analysis**: Uses AWS Bedrock (Claude 3.5 Sonnet) to analyze activities and provide:
  - Performance assessments
  - Health and fitness insights
  - Training recommendations
  - Comparative analysis with historical data
- **OAuth 1.0a Authentication**: Secure user authorization flow
- **Event-Driven Architecture**: Serverless processing with Lambda and EventBridge
- **Scalable Storage**: DynamoDB for activities and user tokens

## 🏗️ Architecture

```
┌──────────────┐         Webhook         ┌─────────────────┐
│   Garmin     │─────────────────────────>│  API Gateway    │
│   Connect    │                          │   /webhook      │
└──────────────┘                          └────────┬────────┘
                                                   │
                                                   ▼
                            ┌──────────────────────────────────┐
                            │  Lambda: Webhook Handler         │
                            │  - Validates payload             │
                            │  - Stores metadata in DynamoDB   │
                            │  - Triggers EventBridge event    │
                            └────────────┬─────────────────────┘
                                         │
                                         ▼
                            ┌──────────────────────────────────┐
                            │  EventBridge: NewActivityReceived│
                            └────────────┬─────────────────────┘
                                         │
                                         ▼
                            ┌──────────────────────────────────┐
                            │  Lambda: Fetch Activity          │
                            │  - Calls Garmin Health API       │
                            │  - Retrieves detailed metrics    │
                            │  - Updates DynamoDB              │
                            │  - Triggers analysis event       │
                            └────────────┬─────────────────────┘
                                         │
                                         ▼
                            ┌──────────────────────────────────┐
                            │  EventBridge: ActivityDataReady  │
                            └────────────┬─────────────────────┘
                                         │
                                         ▼
                            ┌──────────────────────────────────┐
                            │  Lambda: AI Analyzer             │
                            │  - Analyzes activity with        │
                            │    AWS Bedrock (Claude)          │
                            │  - Stores AI insights            │
                            └──────────────────────────────────┘
```

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **Garmin Developer Account**: Register at https://developer.garmin.com/
3. **Tools Installed**:
   - Terraform >= 1.5
   - AWS CLI >= 2.0
   - Python >= 3.11
   - pip

## 🚀 Quick Start

### Step 1: Clone and Configure

```bash
cd 01-personal/aws-ai-agent/src/garmin-integration

# Copy and configure Terraform variables
cp config/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your values
```

### Step 2: Set Up Garmin Developer Account

1. Visit https://developer.garmin.com/
2. Create a new application
3. Note your **Consumer Key** and **Consumer Secret**
4. Add these to your `terraform.tfvars` file

### Step 3: Deploy Infrastructure

```bash
# Run the deployment script
./scripts/deploy.sh
```

This script will:
- Build Lambda layer with dependencies
- Initialize Terraform
- Create all AWS resources
- Display deployment outputs

### Step 4: Register Webhook with Garmin

After deployment, register your webhook URL with Garmin:

```bash
# Get your webhook URL from Terraform outputs
cd terraform
terraform output webhook_url

# Register with Garmin (requires OAuth token)
curl -X POST "https://apis.garmin.com/wellness-api/rest/backfill/activitySummaries" \
  -H "Authorization: OAuth ..." \
  -d "webhookUrl=YOUR_WEBHOOK_URL"
```

### Step 5: Test the Integration

```bash
# Test all endpoints
./scripts/test_endpoints.sh

# Or test OAuth flow programmatically
export API_GATEWAY_URL=$(cd terraform && terraform output -raw api_gateway_stage_invoke_url)
python3 tests/test_oauth_flow.py
```

## 📁 Project Structure

```
garmin-integration/
├── lambda/                      # Lambda function source code
│   ├── garmin_webhook_handler.py    # Receives Garmin webhooks
│   ├── garmin_fetch_activity.py     # Fetches activity details from Garmin API
│   ├── garmin_ai_analyzer.py        # AI analysis with Bedrock
│   ├── garmin_oauth_handler.py      # OAuth 1.0a authentication
│   └── requirements.txt             # Python dependencies
│
├── terraform/                   # Infrastructure as Code
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Variable definitions
│   ├── dynamodb.tf             # DynamoDB tables
│   ├── lambda.tf               # Lambda functions
│   ├── iam.tf                  # IAM roles and policies
│   ├── api_gateway.tf          # API Gateway configuration
│   ├── eventbridge.tf          # EventBridge rules
│   ├── secrets.tf              # Secrets Manager
│   └── outputs.tf              # Terraform outputs
│
├── scripts/                     # Deployment and testing scripts
│   ├── deploy.sh               # Main deployment script
│   ├── destroy.sh              # Destroy infrastructure
│   └── test_endpoints.sh       # Test API endpoints
│
├── tests/                       # Testing utilities
│   ├── test_oauth_flow.py      # Test OAuth flow
│   └── query_activities.py     # Query and view activities
│
├── config/                      # Configuration files
│   ├── terraform.tfvars.example
│   └── .env.example
│
└── README.md                    # This file
```

## 🔧 Configuration

### Terraform Variables

Key variables in `terraform.tfvars`:

```hcl
# AWS Configuration
aws_region  = "us-east-1"
environment = "dev"

# Garmin API Credentials
garmin_consumer_key    = "your-consumer-key"
garmin_consumer_secret = "your-consumer-secret"

# Bedrock Configuration
bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Optional: Use Bedrock Agent instead of direct model
bedrock_agent_id       = "your-agent-id"
bedrock_agent_alias_id = "your-alias-id"
```

### Environment Variables

For local testing, create `.env`:

```bash
AWS_REGION=us-east-1
ACTIVITIES_TABLE_NAME=garmin-integration-activities-dev
TOKENS_TABLE_NAME=garmin-integration-user-tokens-dev
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

## 🔐 OAuth Flow

### User Authorization

1. **Initiate OAuth**:
```bash
curl -X POST "$API_GATEWAY_URL/oauth/initiate" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'
```

Response:
```json
{
  "authorization_url": "https://connect.garmin.com/oauthConfirm?oauth_token=...",
  "message": "Redirect user to authorization_url to complete OAuth"
}
```

2. **User Authorizes**: Redirect user to `authorization_url`

3. **Callback**: Garmin redirects to your callback URL with `oauth_token` and `oauth_verifier`

4. **Token Exchange**: Lambda automatically exchanges for access token and stores in DynamoDB

## 📊 Querying Activities

### View All Activities

```bash
python3 tests/query_activities.py --limit 10
```

### View User's Activities

```bash
python3 tests/query_activities.py --user-token "user_123_abc" --limit 5
```

### View Specific Activity

```bash
python3 tests/query_activities.py --activity-id "12345678"
```

## 🧪 Testing

### Test Endpoints

```bash
./scripts/test_endpoints.sh
```

### Simulate Webhook

```bash
curl -X POST "$API_GATEWAY_URL/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "userAccessToken": "test_token",
    "activitySummaries": [{
      "summaryId": "12345",
      "activityType": "RUNNING",
      "startTimeInSeconds": 1705968000,
      "durationInSeconds": 3600,
      "distanceInMeters": 10000,
      "activeKilocalories": 650,
      "averageHeartRateInBeatsPerMinute": 145
    }]
  }'
```

## 📈 Monitoring

### CloudWatch Logs

View logs for each Lambda function:

```bash
# Webhook handler logs
aws logs tail /aws/lambda/garmin-integration-webhook-handler-dev --follow

# Activity fetcher logs
aws logs tail /aws/lambda/garmin-integration-fetch-activity-dev --follow

# AI analyzer logs
aws logs tail /aws/lambda/garmin-integration-ai-analyzer-dev --follow
```

### DynamoDB Tables

Monitor activities:

```bash
aws dynamodb scan --table-name garmin-integration-activities-dev --limit 5
```

### EventBridge Metrics

View EventBridge metrics in CloudWatch for:
- `garmin-integration-new-activity-dev`
- `garmin-integration-activity-data-ready-dev`

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/webhook` | POST | Receive Garmin webhooks |
| `/oauth/initiate` | POST | Start OAuth flow |
| `/oauth/callback` | GET | OAuth callback |

## 💡 AI Analysis Output

The AI analyzer provides comprehensive insights including:

1. **Performance Assessment**
   - Overall evaluation
   - Strengths and areas for improvement

2. **Health & Fitness Insights**
   - Cardiovascular fitness indicators
   - Heart rate zone analysis
   - Training load assessment
   - Recovery recommendations

3. **Training Recommendations**
   - Suggested next workouts
   - Training focus areas
   - Goal-based advice

4. **Comparative Analysis**
   - Comparison with typical performance
   - Progression indicators
   - Historical trends

5. **Notable Observations**
   - Concerns or achievements
   - Data quality issues

## 🔄 Update and Redeploy

To update Lambda functions:

```bash
# Make your code changes, then:
cd terraform
terraform apply
```

To update only Lambda functions without affecting other resources:

```bash
terraform apply -target=aws_lambda_function.webhook_handler
```

## 🗑️ Cleanup

To destroy all infrastructure:

```bash
./scripts/destroy.sh
```

⚠️ **Warning**: This will delete all data including activities in DynamoDB!

## 🐛 Troubleshooting

### Webhook Not Receiving Data

1. Check API Gateway logs:
```bash
aws logs tail /aws/apigateway/garmin-integration-dev --follow
```

2. Verify webhook is registered with Garmin
3. Check Lambda function permissions

### OAuth Flow Failing

1. Verify Garmin credentials in Secrets Manager:
```bash
aws secretsmanager get-secret-value --secret-id garmin-integration-garmin-credentials-dev
```

2. Check callback URL matches in Garmin Developer Console
3. Verify Lambda has correct environment variables

### AI Analysis Not Generating

1. Check Bedrock permissions in IAM role
2. Verify Bedrock model availability in your region
3. Check Lambda timeout (may need to increase for Bedrock)
4. View AI analyzer logs for errors

### DynamoDB Errors

1. Verify table names in Lambda environment variables
2. Check IAM permissions for DynamoDB access
3. Verify GSI (Global Secondary Index) exists

## 📚 Additional Resources

- [Garmin Health API Documentation](https://developer.garmin.com/health-api/overview/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [OAuth 1.0a Specification](https://oauth.net/core/1.0a/)

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

## 📄 License

This project is for educational and personal use.

## 🔒 Security Notes

- Never commit `terraform.tfvars` or `.env` files
- Rotate Garmin API credentials regularly
- Use AWS Secrets Manager for sensitive data
- Enable AWS CloudTrail for audit logging
- Implement API Gateway throttling in production
- Use AWS WAF for API Gateway protection

## 📞 Support

For issues related to:
- **Garmin API**: Contact Garmin Developer Support
- **AWS Services**: Check AWS Documentation
- **This Integration**: Open an issue in the repository

---

Built with ❤️ using AWS Serverless Technologies and Claude AI
