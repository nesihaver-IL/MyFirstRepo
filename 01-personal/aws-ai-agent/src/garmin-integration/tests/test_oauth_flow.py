#!/usr/bin/env python3
"""
Test OAuth Flow

This script tests the complete OAuth flow for Garmin Connect integration.
"""

import os
import sys
import requests
import json
from typing import Dict, Any

# API Gateway URL - set this after deployment
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod')


def test_oauth_initiate(user_id: str) -> Dict[str, Any]:
    """
    Test OAuth initiation endpoint.

    Args:
        user_id: User identifier for testing

    Returns:
        Response from OAuth initiate endpoint
    """
    url = f"{API_GATEWAY_URL}/oauth/initiate"

    payload = {
        "user_id": user_id
    }

    print(f"\n{'='*60}")
    print("Testing OAuth Initiation")
    print(f"{'='*60}")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('authorization_url')

            print("\n✅ OAuth initiation successful!")
            print(f"\nNext step: Visit this URL to authorize:")
            print(f"{auth_url}")
            print("\nAfter authorizing, you will be redirected to the callback URL.")

            return data
        else:
            print(f"\n❌ OAuth initiation failed!")
            return {}

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {}


def test_webhook_simulation(user_token: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate webhook from Garmin.

    Args:
        user_token: User access token
        activity_data: Activity summary data

    Returns:
        Response from webhook endpoint
    """
    url = f"{API_GATEWAY_URL}/webhook"

    payload = {
        "userAccessToken": user_token,
        "activitySummaries": [activity_data]
    }

    print(f"\n{'='*60}")
    print("Testing Webhook Endpoint")
    print(f"{'='*60}")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()

    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ Webhook test successful!")
            return response.json()
        else:
            print(f"\n❌ Webhook test failed!")
            return {}

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return {}


def test_health_check() -> bool:
    """
    Test health check endpoint.

    Returns:
        True if health check passes, False otherwise
    """
    url = f"{API_GATEWAY_URL}/health"

    print(f"\n{'='*60}")
    print("Testing Health Check")
    print(f"{'='*60}")
    print(f"GET {url}")
    print()

    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✅ Health check passed!")
            return True
        else:
            print(f"\n❌ Health check failed!")
            return False

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def main():
    """Main test runner."""
    if API_GATEWAY_URL == 'https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/prod':
        print("❌ Error: Please set the API_GATEWAY_URL environment variable")
        print("Example: export API_GATEWAY_URL=https://abc123.execute-api.us-east-1.amazonaws.com/prod")
        sys.exit(1)

    print("\n🚀 Starting Garmin Integration Tests")
    print(f"API Gateway URL: {API_GATEWAY_URL}")

    # Test 1: Health Check
    health_ok = test_health_check()
    if not health_ok:
        print("\n⚠️  Health check failed. Stopping tests.")
        sys.exit(1)

    # Test 2: OAuth Initiation
    user_id = f"test_user_{os.getpid()}"
    oauth_data = test_oauth_initiate(user_id)

    # Test 3: Webhook Simulation (with sample data)
    sample_activity = {
        "summaryId": "9876543210",
        "activityType": "RUNNING",
        "startTimeInSeconds": 1705968000,
        "durationInSeconds": 3600,
        "distanceInMeters": 10000,
        "activeKilocalories": 650,
        "averageHeartRateInBeatsPerMinute": 145,
        "maxHeartRateInBeatsPerMinute": 175
    }

    test_webhook_simulation("test_token_123", sample_activity)

    print(f"\n{'='*60}")
    print("Tests Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
