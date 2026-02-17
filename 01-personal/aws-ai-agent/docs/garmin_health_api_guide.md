# Garmin Connect API Integration Guide

Complete guide for integrating with Garmin Connect using different approaches.

---

## Overview of Options

| Option | Difficulty | Cost | Time to Setup | Production Ready | Use Case |
|--------|-----------|------|---------------|------------------|----------|
| **1. Unofficial Python Library** | Easy | Free | 30 minutes | ❌ No | Personal projects, POC, learning |
| **2. Official Garmin Health API** | Hard | Enterprise | 2-8 weeks | ✅ Yes | Commercial apps, production |
| **3. Manual Export** | Medium | Free | 1 hour | ❌ No | One-time analysis, backup |

---

## Option 1: Unofficial Python Library (garminconnect)

### Quick Start

```bash
# Install the library
pip install garminconnect

# Set environment variables
export GARMIN_EMAIL="your@email.com"
export GARMIN_PASSWORD="yourpassword"

# Run the example
python garmin_integration_example.py
```

### Pros & Cons

**Advantages:**
- ✅ **Immediate access** - Works in minutes
- ✅ **Free** - No API fees or approval process
- ✅ **Full data access** - All your personal Garmin data
- ✅ **Active community** - Well-maintained GitHub project
- ✅ **Python-friendly** - Easy integration with AWS Lambda

**Disadvantages:**
- ❌ **Unofficial** - Could break if Garmin changes their website
- ❌ **Not for production** - Violates Garmin's Terms of Service for commercial use
- ❌ **Security concerns** - Must store Garmin password
- ❌ **Rate limiting** - Potential for account suspension if overused
- ❌ **No OAuth** - Can't grant access to other users' data

### When to Use

- Personal fitness tracking projects
- Proof of concept for ideas
- Learning and experimentation
- Internal tools for yourself
- Hackathons and rapid prototyping

### Security Best Practices

```bash
# Store credentials in AWS Secrets Manager
aws secretsmanager create-secret \
    --name health-insights/garmin-credentials \
    --description "Garmin Connect credentials" \
    --secret-string '{
        "email": "your@email.com",
        "password": "your_secure_password"
    }'

# Add rotation schedule (every 90 days)
aws secretsmanager rotate-secret \
    --secret-id health-insights/garmin-credentials \
    --rotation-lambda-arn arn:aws:lambda:region:account:function:RotateGarminSecret \
    --rotation-rules AutomaticallyAfterDays=90
```

---

## Option 2: Official Garmin Health API (Enterprise)

### What is Garmin Health API?

The **Garmin Health API** is Garmin's official, enterprise-grade API for developers building commercial health and fitness applications.

### Features

- ✅ **OAuth 2.0** - Secure user authorization
- ✅ **Production-ready** - Officially supported by Garmin
- ✅ **Multi-user** - Access data for many users
- ✅ **Webhooks** - Real-time data push notifications
- ✅ **Commercial use** - Compliant with Garmin's terms
- ✅ **SLA guarantees** - Uptime and support commitments

### Data Available

1. **Daily Summaries**
   - Steps, distance, calories
   - Active minutes, floors climbed
   - Heart rate statistics

2. **Activities**
   - Workout details (running, swimming, cycling)
   - GPS tracks and routes
   - Performance metrics

3. **Sleep Data**
   - Sleep stages (deep, light, REM, awake)
   - Sleep scores and insights
   - Sleep duration and quality

4. **Health Metrics**
   - Heart rate (resting, max, zones)
   - Stress levels
   - Body composition
   - Blood oxygen (if device supports)

### Application Process

#### Step 1: Apply for Access

1. **Visit:** https://developer.garmin.com/health-api/overview/
2. **Create Account:** Register as a Garmin developer
3. **Submit Application:**
   - Business details
   - App description
   - Use case and user volume
   - Privacy policy
   - Terms of service

**Timeline:** 2-8 weeks for approval

#### Step 2: Provide Business Information

Required documents:
- Company registration
- Privacy policy URL
- Data handling practices
- Security measures
- HIPAA compliance (if applicable)

#### Step 3: Technical Review

Garmin will review:
- Your app's architecture
- Data storage and security
- User consent flow
- API usage patterns

#### Step 4: Receive API Credentials

Once approved, you'll receive:
- Consumer Key
- Consumer Secret
- Access Token (OAuth)
- API documentation

### Pricing

**Note:** Garmin Health API pricing is not publicly disclosed. You must:
- Contact Garmin directly
- Negotiate based on user volume
- Sign enterprise agreement

**Estimated costs** (based on developer reports):
- Small apps (<1,000 users): $0-500/month
- Medium apps (1,000-10,000 users): $500-2,000/month
- Large apps (>10,000 users): Custom pricing

### OAuth Integration Example

```python
# garmin_health_api_oauth.py
"""
Garmin Health API - Official OAuth Integration
Option 2: Enterprise/Production approach
"""

import requests
from requests_oauthlib import OAuth1Session
import json


class GarminHealthAPI:
    """Official Garmin Health API client using OAuth"""

    def __init__(self, consumer_key: str, consumer_secret: str):
        """
        Initialize Garmin Health API client

        Args:
            consumer_key: Your Garmin API consumer key
            consumer_secret: Your Garmin API consumer secret
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = "https://apis.garmin.com/wellness-api/rest"

        # OAuth session
        self.oauth = OAuth1Session(
            client_key=consumer_key,
            client_secret=consumer_secret
        )

    def get_user_authorization_url(self):
        """
        Step 1: Get authorization URL for user

        Returns:
            Authorization URL to redirect user to
        """
        request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'

        # Get request token
        self.oauth = OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            callback_uri='https://yourapp.com/callback'
        )

        request_token = self.oauth.fetch_request_token(request_token_url)

        # Build authorization URL
        authorization_url = self.oauth.authorization_url(
            'https://connect.garmin.com/oauthConfirm'
        )

        return authorization_url, request_token

    def get_access_token(self, oauth_verifier: str):
        """
        Step 2: Exchange authorization code for access token

        Args:
            oauth_verifier: The verifier code from callback

        Returns:
            Access token and secret
        """
        access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'

        access_token = self.oauth.fetch_access_token(
            access_token_url,
            verifier=oauth_verifier
        )

        return access_token

    def get_daily_summary(self, user_access_token: str, date: str):
        """
        Get daily summary for a user

        Args:
            user_access_token: User's OAuth access token
            date: Date in YYYY-MM-DD format
        """
        url = f"{self.base_url}/dailies"

        oauth = OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=user_access_token['oauth_token'],
            resource_owner_secret=user_access_token['oauth_token_secret']
        )

        response = oauth.get(url, params={'date': date})

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    def get_activities(self, user_access_token: str, start_date: str, end_date: str):
        """Get activities for date range"""
        url = f"{self.base_url}/activities"

        oauth = OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=user_access_token['oauth_token'],
            resource_owner_secret=user_access_token['oauth_token_secret']
        )

        response = oauth.get(url, params={
            'startDate': start_date,
            'endDate': end_date
        })

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")

    def get_sleep_data(self, user_access_token: str, date: str):
        """Get sleep data for a specific date"""
        url = f"{self.base_url}/sleeps"

        oauth = OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=user_access_token['oauth_token'],
            resource_owner_secret=user_access_token['oauth_token_secret']
        )

        response = oauth.get(url, params={'date': date})

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code}")


# Flask example for OAuth callback
from flask import Flask, request, redirect, session

app = Flask(__name__)
app.secret_key = 'your-secret-key'

garmin_api = GarminHealthAPI(
    consumer_key='YOUR_CONSUMER_KEY',
    consumer_secret='YOUR_CONSUMER_SECRET'
)


@app.route('/authorize')
def authorize():
    """Initiate OAuth flow"""
    auth_url, request_token = garmin_api.get_user_authorization_url()

    # Store request token in session
    session['request_token'] = request_token

    # Redirect user to Garmin authorization page
    return redirect(auth_url)


@app.route('/callback')
def callback():
    """Handle OAuth callback"""
    oauth_verifier = request.args.get('oauth_verifier')

    if not oauth_verifier:
        return "Authorization failed", 400

    # Exchange verifier for access token
    access_token = garmin_api.get_access_token(oauth_verifier)

    # Store access token for user (in database)
    session['access_token'] = access_token

    return "Authorization successful! You can now access Garmin data."


@app.route('/get-data')
def get_data():
    """Fetch Garmin data for authorized user"""
    access_token = session.get('access_token')

    if not access_token:
        return redirect('/authorize')

    # Get today's summary
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')

    summary = garmin_api.get_daily_summary(access_token, today)

    return summary
```

### Webhook Setup

```python
# garmin_webhook_handler.py
"""
Handle real-time data push from Garmin Health API
"""

from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)


@app.route('/garmin-webhook', methods=['POST'])
def garmin_webhook():
    """
    Webhook endpoint for Garmin Health API

    Garmin will POST data here when users sync their devices
    """

    # Verify webhook signature
    signature = request.headers.get('X-Garmin-Signature')
    body = request.get_data()

    # Calculate expected signature
    secret = 'YOUR_WEBHOOK_SECRET'
    expected_signature = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if signature != expected_signature:
        return "Invalid signature", 403

    # Process webhook data
    data = request.json

    event_type = data.get('eventType')

    if event_type == 'ACTIVITY_CREATED':
        activity_id = data.get('activityId')
        user_id = data.get('userId')

        # Fetch full activity details
        # Store in DynamoDB
        print(f"New activity {activity_id} for user {user_id}")

    elif event_type == 'SLEEP_CREATED':
        sleep_id = data.get('sleepId')
        user_id = data.get('userId')

        # Fetch sleep details
        # Store in DynamoDB
        print(f"New sleep data {sleep_id} for user {user_id}")

    return jsonify({'status': 'received'}), 200
```

---

## Option 3: Manual Export + Upload

### For One-Time Analysis or Backup

If you just need to analyze historical data or create backups:

#### Step 1: Export from Garmin Connect

1. **Login** to https://connect.garmin.com
2. **Navigate** to Activities
3. **Select activities** you want to export
4. **Click** "Export" → Choose format:
   - **FIT** - Original Garmin format (best)
   - **TCX** - Training Center XML (compatible)
   - **GPX** - GPS Exchange (basic)

#### Step 2: Parse FIT Files

```python
# fit_file_parser.py
"""
Parse Garmin FIT files
"""

from fitparse import FitFile
import json


def parse_fit_file(fit_file_path):
    """Parse a .FIT file and extract activity data"""

    fitfile = FitFile(fit_file_path)

    activity_data = {
        'records': [],
        'laps': [],
        'session': {}
    }

    # Parse all messages
    for record in fitfile.get_messages():
        # Session data (summary)
        if record.name == 'session':
            for field in record.fields:
                activity_data['session'][field.name] = field.value

        # Lap data
        elif record.name == 'lap':
            lap = {}
            for field in record.fields:
                lap[field.name] = field.value
            activity_data['laps'].append(lap)

        # Record data (time series)
        elif record.name == 'record':
            point = {}
            for field in record.fields:
                point[field.name] = field.value
            activity_data['records'].append(point)

    return activity_data


def main():
    # Parse a FIT file
    data = parse_fit_file('activity.fit')

    # Extract key metrics
    session = data['session']

    print(f"Activity Type: {session.get('sport')}")
    print(f"Distance: {session.get('total_distance') / 1000:.2f} km")
    print(f"Duration: {session.get('total_timer_time') / 60:.2f} minutes")
    print(f"Avg Heart Rate: {session.get('avg_heart_rate')} bpm")
    print(f"Calories: {session.get('total_calories')} kcal")

    # Save to JSON
    with open('activity.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)


if __name__ == "__main__":
    main()
```

**Install parser:**
```bash
pip install fitparse
```

#### Step 3: Upload to S3

```bash
# Upload exported files to S3
aws s3 sync ./garmin-exports s3://health-insights-raw-data/garmin/

# Process with Lambda
aws lambda invoke \
    --function-name ProcessGarminExport \
    --payload '{"bucket": "health-insights-raw-data", "key": "garmin/activity.fit"}' \
    response.json
```

---

## Comparison Matrix

### Feature Availability

| Feature | Unofficial Library | Official API | Manual Export |
|---------|-------------------|--------------|---------------|
| Activities | ✅ | ✅ | ✅ |
| Sleep Data | ✅ | ✅ | ✅ |
| Heart Rate | ✅ | ✅ | ✅ |
| GPS Tracks | ✅ | ✅ | ✅ |
| Body Composition | ✅ | ✅ | ❌ |
| Stress Levels | ✅ | ✅ | ❌ |
| Real-time Sync | ✅ (polling) | ✅ (webhooks) | ❌ |
| Multi-user | ❌ | ✅ | ❌ |
| Commercial Use | ❌ | ✅ | ❌ |

### Cost Comparison (Monthly)

| Scenario | Unofficial | Official API | Manual |
|----------|-----------|--------------|--------|
| Personal use (1 user) | Free | $0-100 | Free |
| Small app (<1K users) | N/A | $500-1,000 | N/A |
| Medium app (1K-10K) | N/A | $1,000-2,000 | N/A |
| Enterprise (>10K) | N/A | Custom | N/A |

---

## Recommendations

### For Your Health Insights Agent Project

Based on your `HEALTH_INSIGHTS_AGENT_PLAN.md`, here's my recommendation:

**Phase 1 (POC/Development): Use Unofficial Library**
- Quick to implement
- Free during development
- Full access to your personal data
- Perfect for testing the concept

**Phase 2 (Production): Migrate to Official API**
- Apply for Garmin Health API access
- Implement OAuth flow
- Migrate data pipeline
- Enable multi-user support

### Implementation Timeline

```
Week 1-2: POC with Unofficial Library
├─ Implement garminconnect integration
├─ Set up Lambda data fetcher
├─ Test with your personal data
└─ Validate agent functionality

Week 3-4: Apply for Official API
├─ Submit Garmin Health API application
├─ Prepare privacy policy
├─ Design OAuth flow
└─ Wait for approval (2-8 weeks)

Week 5-6: Migrate to Official API (once approved)
├─ Implement OAuth authentication
├─ Update Lambda functions
├─ Set up webhooks
└─ Test with beta users
```

---

## Security Considerations

### For Unofficial Library

1. **Store credentials securely** in AWS Secrets Manager
2. **Rotate passwords** every 90 days
3. **Use encryption** at rest and in transit
4. **Limit access** to personal use only
5. **Monitor** for unusual activity

### For Official API

1. **Implement OAuth 2.0** properly
2. **Never store** user passwords
3. **Request minimal scopes** needed
4. **Implement token refresh** logic
5. **Use HTTPS** exclusively
6. **Validate webhook** signatures
7. **Comply with GDPR/CCPA** if applicable

---

## Next Steps

1. **Start with unofficial library** for immediate development
2. **Apply for official API** if planning commercial use
3. **Implement data fetcher** Lambda function
4. **Set up DynamoDB** storage
5. **Test with AWS Bedrock** agent integration

See `garmin_integration_example.py` for working code examples!

---

**Resources:**
- Unofficial Library: https://github.com/cyberjunky/python-garminconnect
- Official API: https://developer.garmin.com/health-api/
- FIT File SDK: https://developer.garmin.com/fit/overview/
