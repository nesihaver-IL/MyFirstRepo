"""
Garmin Webhook Handler Lambda Function

This function receives webhook notifications from Garmin Health API when
new activities are uploaded to Garmin Connect.

Environment Variables:
    ACTIVITIES_TABLE_NAME: DynamoDB table for storing activities
    EVENT_BUS_NAME: EventBridge event bus name (default: 'default')
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# Environment variables
ACTIVITIES_TABLE = os.environ.get('ACTIVITIES_TABLE_NAME', 'garmin-activities')
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'default')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_webhook_payload(body: Dict[str, Any]) -> bool:
    """
    Validate the incoming webhook payload from Garmin.

    Args:
        body: Parsed JSON body from webhook request

    Returns:
        True if payload is valid, False otherwise
    """
    required_fields = ['userAccessToken']
    for field in required_fields:
        if field not in body:
            logger.error(f"Missing required field: {field}")
            return False
    return True


def store_activity_metadata(activity: Dict[str, Any], user_token: str) -> None:
    """
    Store activity metadata in DynamoDB.

    Args:
        activity: Activity data from Garmin webhook
        user_token: User's access token
    """
    table = dynamodb.Table(ACTIVITIES_TABLE)

    activity_id = activity.get('summaryId')

    item = {
        'activity_id': str(activity_id),
        'user_token': user_token,
        'activity_type': activity.get('activityType', 'UNKNOWN'),
        'start_time': activity.get('startTimeInSeconds', 0),
        'timestamp': datetime.utcnow().isoformat(),
        'processed': False,
        'raw_data': json.dumps(activity),
        'status': 'received'
    }

    # Add optional fields if present
    if 'durationInSeconds' in activity:
        item['duration_seconds'] = activity['durationInSeconds']
    if 'distanceInMeters' in activity:
        item['distance_meters'] = activity['distanceInMeters']

    table.put_item(Item=item)
    logger.info(f"Stored activity {activity_id} for user {user_token[:10]}...")


def trigger_processing_event(activity: Dict[str, Any], user_token: str) -> None:
    """
    Trigger EventBridge event to start activity processing pipeline.

    Args:
        activity: Activity data from Garmin webhook
        user_token: User's access token
    """
    activity_id = activity.get('summaryId')
    activity_type = activity.get('activityType', 'UNKNOWN')

    event_detail = {
        'activity_id': str(activity_id),
        'user_token': user_token,
        'activity_type': activity_type,
        'start_time': activity.get('startTimeInSeconds', 0),
        'timestamp': datetime.utcnow().isoformat()
    }

    response = eventbridge.put_events(
        Entries=[
            {
                'Source': 'garmin.webhook',
                'DetailType': 'NewActivityReceived',
                'Detail': json.dumps(event_detail),
                'EventBusName': EVENT_BUS_NAME
            }
        ]
    )

    if response['FailedEntryCount'] > 0:
        logger.error(f"Failed to publish event: {response['Entries']}")
        raise Exception("Failed to publish EventBridge event")

    logger.info(f"Triggered processing event for activity {activity_id}")


def process_activity_summaries(summaries: List[Dict[str, Any]], user_token: str) -> Dict[str, Any]:
    """
    Process list of activity summaries from webhook.

    Args:
        summaries: List of activity summaries
        user_token: User's access token

    Returns:
        Processing result summary
    """
    processed_count = 0
    failed_count = 0
    activity_ids = []

    for activity in summaries:
        try:
            activity_id = activity.get('summaryId')

            # Store in DynamoDB
            store_activity_metadata(activity, user_token)

            # Trigger processing event
            trigger_processing_event(activity, user_token)

            processed_count += 1
            activity_ids.append(str(activity_id))

        except Exception as e:
            logger.error(f"Failed to process activity {activity.get('summaryId')}: {str(e)}")
            failed_count += 1

    return {
        'processed': processed_count,
        'failed': failed_count,
        'activity_ids': activity_ids
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for Garmin webhook notifications.

    Args:
        event: Lambda event object containing API Gateway request
        context: Lambda context object

    Returns:
        API Gateway response with status code and body
    """
    logger.info(f"Received webhook event: {json.dumps(event)}")

    try:
        # Parse request body
        if 'body' not in event:
            logger.error("No body in event")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing request body'})
            }

        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        # Validate payload
        if not validate_webhook_payload(body):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid webhook payload'})
            }

        # Extract data
        user_token = body.get('userAccessToken')
        activity_summaries = body.get('activitySummaries', [])

        if not activity_summaries:
            logger.warning("No activity summaries in webhook payload")
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'No activities to process'})
            }

        # Process activities
        result = process_activity_summaries(activity_summaries, user_token)

        logger.info(f"Processed {result['processed']} activities, {result['failed']} failed")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'processed': result['processed'],
                'failed': result['failed'],
                'activity_ids': result['activity_ids']
            })
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }

    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
