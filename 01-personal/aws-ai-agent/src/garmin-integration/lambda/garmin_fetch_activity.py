"""
Garmin Activity Fetcher Lambda Function

This function fetches detailed activity data from Garmin Health API
and stores it in DynamoDB for AI analysis.

Environment Variables:
    TOKENS_TABLE_NAME: DynamoDB table storing user OAuth tokens
    ACTIVITIES_TABLE_NAME: DynamoDB table storing activity data
    GARMIN_CREDENTIALS_SECRET: AWS Secrets Manager secret name for Garmin API credentials
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import requests
from requests_oauthlib import OAuth1

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')
eventbridge = boto3.client('events')

# Environment variables
TOKENS_TABLE = os.environ.get('TOKENS_TABLE_NAME', 'garmin-user-tokens')
ACTIVITIES_TABLE = os.environ.get('ACTIVITIES_TABLE_NAME', 'garmin-activities')
GARMIN_CREDENTIALS_SECRET = os.environ.get('GARMIN_CREDENTIALS_SECRET', 'garmin-api-credentials')
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'default')

# Garmin API configuration
GARMIN_API_BASE = "https://apis.garmin.com/wellness-api/rest"
GARMIN_API_VERSION = "2"

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GarminAPIClient:
    """Client for interacting with Garmin Health API."""

    def __init__(self, consumer_key: str, consumer_secret: str):
        """
        Initialize Garmin API client.

        Args:
            consumer_key: OAuth consumer key
            consumer_secret: OAuth consumer secret
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = GARMIN_API_BASE

    def _get_oauth_auth(self, access_token: str, access_token_secret: str) -> OAuth1:
        """
        Create OAuth1 authentication object.

        Args:
            access_token: User's OAuth access token
            access_token_secret: User's OAuth access token secret

        Returns:
            OAuth1 authentication object
        """
        return OAuth1(
            self.consumer_key,
            self.consumer_secret,
            access_token,
            access_token_secret,
            signature_type='auth_header'
        )

    def get_activity_summary(self, activity_id: str, access_token: str, access_token_secret: str) -> Dict[str, Any]:
        """
        Fetch activity summary from Garmin API.

        Args:
            activity_id: Garmin activity ID
            access_token: User's OAuth access token
            access_token_secret: User's OAuth access token secret

        Returns:
            Activity summary data

        Raises:
            Exception: If API request fails
        """
        url = f"{self.base_url}/activitySummary/{activity_id}"
        auth = self._get_oauth_auth(access_token, access_token_secret)

        logger.info(f"Fetching activity summary for activity {activity_id}")

        response = requests.get(url, auth=auth, timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise Exception(f"Activity {activity_id} not found")
        elif response.status_code == 401:
            raise Exception("Unauthorized - invalid OAuth credentials")
        else:
            raise Exception(f"Failed to fetch activity: HTTP {response.status_code} - {response.text}")

    def get_activity_details(self, activity_id: str, access_token: str, access_token_secret: str) -> Dict[str, Any]:
        """
        Fetch detailed activity data including heart rate zones, laps, etc.

        Args:
            activity_id: Garmin activity ID
            access_token: User's OAuth access token
            access_token_secret: User's OAuth access token secret

        Returns:
            Detailed activity data

        Raises:
            Exception: If API request fails
        """
        url = f"{self.base_url}/activityDetails/{activity_id}"
        auth = self._get_oauth_auth(access_token, access_token_secret)

        logger.info(f"Fetching activity details for activity {activity_id}")

        response = requests.get(url, auth=auth, timeout=30)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Activity details not found for {activity_id}")
            return {}
        else:
            logger.warning(f"Could not fetch activity details: HTTP {response.status_code}")
            return {}


def get_garmin_credentials() -> Dict[str, str]:
    """
    Retrieve Garmin API credentials from AWS Secrets Manager.

    Returns:
        Dictionary with consumer_key and consumer_secret

    Raises:
        Exception: If credentials cannot be retrieved
    """
    try:
        response = secrets_client.get_secret_value(SecretId=GARMIN_CREDENTIALS_SECRET)
        secret_string = response['SecretString']
        credentials = json.loads(secret_string)

        if 'consumer_key' not in credentials or 'consumer_secret' not in credentials:
            raise Exception("Invalid credentials format in Secrets Manager")

        return credentials

    except Exception as e:
        logger.error(f"Failed to retrieve Garmin credentials: {str(e)}")
        raise


def get_user_tokens(user_token: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user's OAuth tokens from DynamoDB.

    Args:
        user_token: User's access token identifier

    Returns:
        User token data or None if not found
    """
    try:
        table = dynamodb.Table(TOKENS_TABLE)
        response = table.get_item(Key={'user_token': user_token})
        return response.get('Item')

    except Exception as e:
        logger.error(f"Failed to retrieve user tokens: {str(e)}")
        return None


def extract_activity_metrics(activity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize activity metrics from Garmin API response.

    Args:
        activity_data: Raw activity data from Garmin API

    Returns:
        Normalized metrics dictionary
    """
    metrics = {
        'activity_id': str(activity_data.get('summaryId', '')),
        'activity_type': activity_data.get('activityType', 'UNKNOWN'),
        'start_time': activity_data.get('startTimeInSeconds', 0),
        'duration_seconds': activity_data.get('durationInSeconds', 0),
        'distance_meters': activity_data.get('distanceInMeters', 0),
        'calories': activity_data.get('activeKilocalories', 0),
    }

    # Heart rate data
    if 'averageHeartRateInBeatsPerMinute' in activity_data:
        metrics['avg_heart_rate'] = activity_data['averageHeartRateInBeatsPerMinute']
    if 'maxHeartRateInBeatsPerMinute' in activity_data:
        metrics['max_heart_rate'] = activity_data['maxHeartRateInBeatsPerMinute']

    # Additional metrics
    if 'steps' in activity_data:
        metrics['steps'] = activity_data['steps']
    if 'elevationGainInMeters' in activity_data:
        metrics['elevation_gain'] = activity_data['elevationGainInMeters']
    if 'elevationLossInMeters' in activity_data:
        metrics['elevation_loss'] = activity_data['elevationLossInMeters']
    if 'averagePaceInMinutesPerKilometer' in activity_data:
        metrics['avg_pace_min_per_km'] = activity_data['averagePaceInMinutesPerKilometer']
    if 'averageSpeedInMetersPerSecond' in activity_data:
        metrics['avg_speed_m_per_s'] = activity_data['averageSpeedInMetersPerSecond']

    # Location data
    if 'startingLatitudeInDegree' in activity_data and 'startingLongitudeInDegree' in activity_data:
        metrics['start_location'] = {
            'lat': activity_data['startingLatitudeInDegree'],
            'lon': activity_data['startingLongitudeInDegree']
        }

    # Cadence
    if 'averageBikingCadenceInRoundsPerMinute' in activity_data:
        metrics['avg_cadence'] = activity_data['averageBikingCadenceInRoundsPerMinute']
    elif 'averageRunningCadenceInStepsPerMinute' in activity_data:
        metrics['avg_cadence'] = activity_data['averageRunningCadenceInStepsPerMinute']

    # Training effect
    if 'trainingEffect' in activity_data:
        metrics['training_effect'] = activity_data['trainingEffect']

    return metrics


def update_activity_in_dynamodb(activity_id: str, metrics: Dict[str, Any], raw_data: Dict[str, Any]) -> None:
    """
    Update activity record in DynamoDB with fetched data.

    Args:
        activity_id: Activity ID
        metrics: Extracted metrics
        raw_data: Raw API response data
    """
    table = dynamodb.Table(ACTIVITIES_TABLE)

    table.update_item(
        Key={'activity_id': activity_id},
        UpdateExpression='SET metrics = :m, raw_detail = :r, #status = :s, fetched_at = :f',
        ExpressionAttributeNames={
            '#status': 'status'
        },
        ExpressionAttributeValues={
            ':m': metrics,
            ':r': json.dumps(raw_data),
            ':s': 'fetched',
            ':f': datetime.utcnow().isoformat()
        }
    )

    logger.info(f"Updated activity {activity_id} in DynamoDB")


def trigger_ai_analysis_event(activity_id: str, metrics: Dict[str, Any]) -> None:
    """
    Trigger EventBridge event for AI analysis.

    Args:
        activity_id: Activity ID
        metrics: Activity metrics
    """
    event_detail = {
        'activity_id': activity_id,
        'metrics': metrics,
        'timestamp': datetime.utcnow().isoformat()
    }

    response = eventbridge.put_events(
        Entries=[
            {
                'Source': 'garmin.activity-fetcher',
                'DetailType': 'ActivityDataReady',
                'Detail': json.dumps(event_detail),
                'EventBusName': EVENT_BUS_NAME
            }
        ]
    )

    if response['FailedEntryCount'] > 0:
        logger.error(f"Failed to publish AI analysis event: {response['Entries']}")
        raise Exception("Failed to publish EventBridge event")

    logger.info(f"Triggered AI analysis event for activity {activity_id}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for fetching Garmin activity details.

    This function is triggered by EventBridge when a new activity is detected.

    Args:
        event: EventBridge event containing activity information
        context: Lambda context object

    Returns:
        Processing result
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract event details
        detail = event.get('detail', {})
        activity_id = detail.get('activity_id')
        user_token = detail.get('user_token')

        if not activity_id or not user_token:
            raise ValueError("Missing activity_id or user_token in event")

        # Get Garmin API credentials
        credentials = get_garmin_credentials()

        # Get user OAuth tokens
        user_oauth = get_user_tokens(user_token)
        if not user_oauth:
            raise Exception(f"User tokens not found for {user_token}")

        # Initialize Garmin API client
        api_client = GarminAPIClient(
            credentials['consumer_key'],
            credentials['consumer_secret']
        )

        # Fetch activity summary
        activity_summary = api_client.get_activity_summary(
            activity_id,
            user_oauth['access_token'],
            user_oauth['access_token_secret']
        )

        # Fetch activity details (optional - may not be available for all activities)
        activity_details = api_client.get_activity_details(
            activity_id,
            user_oauth['access_token'],
            user_oauth['access_token_secret']
        )

        # Merge summary and details
        complete_data = {**activity_summary, **activity_details}

        # Extract metrics
        metrics = extract_activity_metrics(complete_data)

        # Update DynamoDB
        update_activity_in_dynamodb(activity_id, metrics, complete_data)

        # Trigger AI analysis
        trigger_ai_analysis_event(activity_id, metrics)

        return {
            'statusCode': 200,
            'activity_id': activity_id,
            'metrics': metrics
        }

    except Exception as e:
        logger.error(f"Error fetching activity: {str(e)}", exc_info=True)

        # Update activity status to failed
        if 'activity_id' in locals():
            try:
                table = dynamodb.Table(ACTIVITIES_TABLE)
                table.update_item(
                    Key={'activity_id': activity_id},
                    UpdateExpression='SET #status = :s, error_message = :e',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':s': 'failed',
                        ':e': str(e)
                    }
                )
            except Exception as update_error:
                logger.error(f"Failed to update error status: {str(update_error)}")

        raise
