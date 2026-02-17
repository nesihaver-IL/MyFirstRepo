"""
Garmin Connect Integration - Unofficial Python Library Example
Option 1: Using garminconnect library (RECOMMENDED for POC)

Installation:
pip install garminconnect

This example shows how to authenticate and fetch data from Garmin Connect.
"""

import json
from datetime import datetime, timedelta
from garminconnect import Garmin, GarminConnectAuthenticationError


class GarminConnectClient:
    """Wrapper for Garmin Connect API using unofficial library"""

    def __init__(self, email: str, password: str):
        """
        Initialize Garmin Connect client

        Args:
            email: Your Garmin Connect email
            password: Your Garmin Connect password
        """
        self.client = Garmin(email, password)
        self.is_authenticated = False

    def authenticate(self):
        """Login to Garmin Connect"""
        try:
            self.client.login()
            self.is_authenticated = True
            print("✅ Successfully authenticated with Garmin Connect")
            return True
        except GarminConnectAuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            return False

    def get_user_summary(self):
        """Get user profile summary"""
        if not self.is_authenticated:
            raise Exception("Not authenticated. Call authenticate() first.")

        return self.client.get_full_name()

    def get_activities(self, start=0, limit=50):
        """
        Get recent activities

        Args:
            start: Starting index (0 = most recent)
            limit: Number of activities to fetch (max 100)

        Returns:
            List of activity dictionaries
        """
        activities = self.client.get_activities(start, limit)
        return activities

    def get_swimming_activities(self, days=30):
        """Get swimming activities from last N days"""
        activities = self.get_activities(0, 100)

        # Filter for swimming
        swimming_types = ['lap_swimming', 'open_water_swimming', 'swimming']
        swimming_activities = [
            a for a in activities
            if a.get('activityType', {}).get('typeKey') in swimming_types
        ]

        return swimming_activities[:days]

    def get_running_activities(self, days=30):
        """Get running activities from last N days"""
        activities = self.get_activities(0, 100)

        # Filter for running
        running_types = ['running', 'trail_running', 'treadmill_running', 'track_running']
        running_activities = [
            a for a in activities
            if a.get('activityType', {}).get('typeKey') in running_types
        ]

        return running_activities[:days]

    def get_activity_details(self, activity_id):
        """
        Get detailed information for a specific activity

        Args:
            activity_id: The activity ID
        """
        return self.client.get_activity_evaluation(activity_id)

    def get_sleep_data(self, date=None):
        """
        Get sleep data for a specific date

        Args:
            date: Date string in 'YYYY-MM-DD' format (default: today)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        sleep_data = self.client.get_sleep_data(date)
        return sleep_data

    def get_steps_data(self, date=None):
        """Get daily step count"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        steps = self.client.get_steps_data(date)
        return steps

    def get_heart_rate_data(self, date=None):
        """Get heart rate data for a date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        hr_data = self.client.get_heart_rates(date)
        return hr_data

    def get_body_composition(self, date=None):
        """Get body composition data (weight, body fat, etc.)"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        weight_data = self.client.get_body_composition(date)
        return weight_data


# ============================================================
# AWS Lambda Integration Example
# ============================================================

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch Garmin data
    Triggered by EventBridge (hourly or daily)

    Environment variables needed:
    - GARMIN_EMAIL: Your Garmin Connect email
    - GARMIN_PASSWORD: Your Garmin Connect password (from Secrets Manager)
    """
    import os
    import boto3

    # Get credentials from Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId='garmin-credentials')
    credentials = json.loads(secret['SecretString'])

    email = credentials['email']
    password = credentials['password']

    # Initialize Garmin client
    garmin = GarminConnectClient(email, password)

    # Authenticate
    if not garmin.authenticate():
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Authentication failed'})
        }

    # Fetch recent data
    try:
        # Get swimming activities
        swimming = garmin.get_swimming_activities(days=7)
        print(f"Found {len(swimming)} swimming activities")

        # Get running activities
        running = garmin.get_running_activities(days=7)
        print(f"Found {len(running)} running activities")

        # Get today's sleep data
        sleep = garmin.get_sleep_data()
        print(f"Sleep data: {sleep}")

        # Store in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        activities_table = dynamodb.Table('HealthInsights-Activities')
        sleep_table = dynamodb.Table('HealthInsights-SleepData')

        # Store swimming activities
        for activity in swimming:
            activities_table.put_item(Item={
                'userId': 'user123',  # Get from context
                'activityId': str(activity['activityId']),
                'timestamp': activity['startTimeLocal'],
                'activityType': 'swimming',
                'duration': activity.get('duration', 0),
                'distance': activity.get('distance', 0),
                'rawData': activity
            })

        # Store running activities
        for activity in running:
            activities_table.put_item(Item={
                'userId': 'user123',
                'activityId': str(activity['activityId']),
                'timestamp': activity['startTimeLocal'],
                'activityType': 'running',
                'duration': activity.get('duration', 0),
                'distance': activity.get('distance', 0),
                'rawData': activity
            })

        # Store sleep data
        if sleep:
            sleep_table.put_item(Item={
                'userId': 'user123',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'totalSleep': sleep.get('sleepTimeSeconds', 0),
                'deepSleep': sleep.get('deepSleepSeconds', 0),
                'lightSleep': sleep.get('lightSleepSeconds', 0),
                'remSleep': sleep.get('remSleepSeconds', 0),
                'rawData': sleep
            })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Sync completed successfully',
                'swimming_count': len(swimming),
                'running_count': len(running),
                'sleep_synced': sleep is not None
            })
        }

    except Exception as e:
        print(f"Error fetching data: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


# ============================================================
# Standalone Testing Example
# ============================================================

def main():
    """
    Standalone test script

    Usage:
        python garmin_integration_example.py

    Set these environment variables:
        export GARMIN_EMAIL="your@email.com"
        export GARMIN_PASSWORD="yourpassword"
    """
    import os

    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')

    if not email or not password:
        print("❌ Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")
        return

    # Initialize client
    garmin = GarminConnectClient(email, password)

    # Authenticate
    if not garmin.authenticate():
        print("Failed to authenticate")
        return

    # Get user summary
    print(f"\n👤 User: {garmin.get_user_summary()}")

    # Get recent swimming activities
    print("\n🏊 Swimming Activities (Last 30 days):")
    swimming = garmin.get_swimming_activities(30)
    for activity in swimming[:5]:  # Show first 5
        print(f"  - {activity.get('activityName')} | {activity.get('distance')}m | {activity.get('startTimeLocal')}")

    # Get recent running activities
    print("\n🏃 Running Activities (Last 30 days):")
    running = garmin.get_running_activities(30)
    for activity in running[:5]:  # Show first 5
        distance_km = activity.get('distance', 0) / 1000
        print(f"  - {activity.get('activityName')} | {distance_km:.2f}km | {activity.get('startTimeLocal')}")

    # Get today's sleep data
    print("\n😴 Sleep Data (Last night):")
    sleep = garmin.get_sleep_data()
    if sleep:
        total_hours = sleep.get('sleepTimeSeconds', 0) / 3600
        print(f"  Total sleep: {total_hours:.2f} hours")
        print(f"  Sleep score: {sleep.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')}")

    # Get today's steps
    print("\n👟 Steps Data (Today):")
    steps = garmin.get_steps_data()
    if steps:
        print(f"  Total steps: {steps.get('totalSteps', 0):,}")


if __name__ == "__main__":
    main()
