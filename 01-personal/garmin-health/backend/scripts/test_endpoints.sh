#!/bin/bash
# Test Garmin Integration Endpoints

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get API Gateway URL from Terraform output
cd "$TERRAFORM_DIR"
API_URL=$(terraform output -raw api_gateway_stage_invoke_url 2>/dev/null)

if [ -z "$API_URL" ]; then
    log_error "Could not retrieve API Gateway URL. Make sure infrastructure is deployed."
    exit 1
fi

log_info "API Gateway URL: $API_URL"
echo ""

# Test health endpoint
log_info "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_URL/health")
HTTP_STATUS=$(echo "$HEALTH_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Health check passed"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}✗${NC} Health check failed (HTTP $HTTP_STATUS)"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test OAuth initiate endpoint
log_info "Testing OAuth initiate endpoint..."
TEST_USER_ID="test_user_$(date +%s)"

OAUTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "$API_URL/oauth/initiate" \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"$TEST_USER_ID\"}")

HTTP_STATUS=$(echo "$OAUTH_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$OAUTH_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} OAuth initiate passed"
    echo "Response: $RESPONSE_BODY"

    # Extract authorization URL
    AUTH_URL=$(echo "$RESPONSE_BODY" | grep -o '"authorization_url":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$AUTH_URL" ]; then
        echo ""
        echo "Authorization URL: $AUTH_URL"
        echo "Visit this URL to complete OAuth flow"
    fi
else
    echo -e "${RED}✗${NC} OAuth initiate failed (HTTP $HTTP_STATUS)"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

# Test webhook endpoint with sample data
log_info "Testing webhook endpoint (with sample data)..."
WEBHOOK_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST "$API_URL/webhook" \
    -H "Content-Type: application/json" \
    -d '{
        "userAccessToken": "test_token_123",
        "activitySummaries": [{
            "summaryId": "12345678",
            "activityType": "RUNNING",
            "startTimeInSeconds": 1642416000,
            "durationInSeconds": 3600,
            "distanceInMeters": 10000
        }]
    }')

HTTP_STATUS=$(echo "$WEBHOOK_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$WEBHOOK_RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Webhook test passed"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}✗${NC} Webhook test failed (HTTP $HTTP_STATUS)"
    echo "Response: $RESPONSE_BODY"
fi
echo ""

log_info "Endpoint testing complete!"
