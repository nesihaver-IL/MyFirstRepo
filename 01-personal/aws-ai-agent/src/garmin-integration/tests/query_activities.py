#!/usr/bin/env python3
"""
Query Garmin Activities from DynamoDB

This script queries activities from the DynamoDB table and displays their analysis.
"""

import boto3
import json
import sys
from typing import List, Dict, Any
from datetime import datetime
from boto3.dynamodb.conditions import Key

# DynamoDB configuration
REGION = 'us-east-1'
ACTIVITIES_TABLE = 'garmin-integration-activities-dev'  # Update with your table name


def get_all_activities(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get all activities from DynamoDB.

    Args:
        limit: Maximum number of activities to retrieve

    Returns:
        List of activity records
    """
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(ACTIVITIES_TABLE)

    try:
        response = table.scan(Limit=limit)
        return response.get('Items', [])
    except Exception as e:
        print(f"Error querying activities: {str(e)}")
        return []


def get_user_activities(user_token: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get activities for a specific user.

    Args:
        user_token: User's access token
        limit: Maximum number of activities to retrieve

    Returns:
        List of activity records for the user
    """
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(ACTIVITIES_TABLE)

    try:
        response = table.query(
            IndexName='user-timestamp-index',
            KeyConditionExpression=Key('user_token').eq(user_token),
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error querying user activities: {str(e)}")
        return []


def get_activity_by_id(activity_id: str) -> Dict[str, Any]:
    """
    Get a specific activity by ID.

    Args:
        activity_id: Activity identifier

    Returns:
        Activity record
    """
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(ACTIVITIES_TABLE)

    try:
        response = table.get_item(Key={'activity_id': activity_id})
        return response.get('Item', {})
    except Exception as e:
        print(f"Error getting activity: {str(e)}")
        return {}


def format_activity(activity: Dict[str, Any]) -> str:
    """
    Format activity for display.

    Args:
        activity: Activity record

    Returns:
        Formatted string
    """
    output = []
    output.append("=" * 80)
    output.append(f"Activity ID: {activity.get('activity_id', 'N/A')}")
    output.append(f"Status: {activity.get('status', 'N/A')}")
    output.append(f"Timestamp: {activity.get('timestamp', 'N/A')}")
    output.append("-" * 80)

    # Metrics
    metrics = activity.get('metrics', {})
    if metrics:
        output.append("METRICS:")
        output.append(f"  Activity Type: {metrics.get('activity_type', 'N/A')}")
        output.append(f"  Duration: {metrics.get('duration_seconds', 0)} seconds")
        output.append(f"  Distance: {metrics.get('distance_meters', 0)} meters")
        output.append(f"  Calories: {metrics.get('calories', 0)} kcal")

        if 'avg_heart_rate' in metrics:
            output.append(f"  Avg Heart Rate: {metrics['avg_heart_rate']} bpm")
        if 'max_heart_rate' in metrics:
            output.append(f"  Max Heart Rate: {metrics['max_heart_rate']} bpm")

        output.append("-" * 80)

    # AI Analysis
    ai_analysis = activity.get('ai_analysis')
    if ai_analysis:
        output.append("AI ANALYSIS:")
        output.append(ai_analysis)
        output.append("-" * 80)
        output.append(f"Analysis Time: {activity.get('analysis_time', 'N/A')}")
    else:
        output.append("AI ANALYSIS: Not yet analyzed")

    output.append("=" * 80)
    output.append("")

    return "\n".join(output)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description='Query Garmin activities from DynamoDB')
    parser.add_argument('--activity-id', help='Get specific activity by ID')
    parser.add_argument('--user-token', help='Get activities for specific user')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of activities to retrieve')
    parser.add_argument('--table', default=ACTIVITIES_TABLE, help='DynamoDB table name')
    parser.add_argument('--region', default=REGION, help='AWS region')

    args = parser.parse_args()

    # Update globals
    global ACTIVITIES_TABLE, REGION
    ACTIVITIES_TABLE = args.table
    REGION = args.region

    print(f"\n🔍 Querying Garmin Activities")
    print(f"Table: {ACTIVITIES_TABLE}")
    print(f"Region: {REGION}\n")

    # Query based on arguments
    if args.activity_id:
        print(f"Fetching activity: {args.activity_id}\n")
        activity = get_activity_by_id(args.activity_id)
        if activity:
            print(format_activity(activity))
        else:
            print("Activity not found.")

    elif args.user_token:
        print(f"Fetching activities for user: {args.user_token}\n")
        activities = get_user_activities(args.user_token, args.limit)

        if activities:
            print(f"Found {len(activities)} activities:\n")
            for activity in activities:
                print(format_activity(activity))
        else:
            print("No activities found for this user.")

    else:
        print(f"Fetching all activities (limit: {args.limit})\n")
        activities = get_all_activities(args.limit)

        if activities:
            print(f"Found {len(activities)} activities:\n")
            for activity in activities:
                print(format_activity(activity))
        else:
            print("No activities found.")


if __name__ == "__main__":
    main()
