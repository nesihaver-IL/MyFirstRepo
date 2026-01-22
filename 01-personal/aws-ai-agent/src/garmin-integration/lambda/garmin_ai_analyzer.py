"""
Garmin AI Analyzer Lambda Function

This function uses AWS Bedrock Agent to analyze Garmin activity data
and provide fitness insights, recommendations, and health assessments.

Environment Variables:
    ACTIVITIES_TABLE_NAME: DynamoDB table storing activity data
    BEDROCK_AGENT_ID: Bedrock Agent ID
    BEDROCK_AGENT_ALIAS_ID: Bedrock Agent Alias ID
    BEDROCK_MODEL_ID: Optional direct model invocation (fallback)
"""

import json
import boto3
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
bedrock_runtime = boto3.client('bedrock-runtime')

# Environment variables
ACTIVITIES_TABLE = os.environ.get('ACTIVITIES_TABLE_NAME', 'garmin-activities')
BEDROCK_AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
BEDROCK_AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ActivityAnalyzer:
    """Analyzes Garmin activity data using AI."""

    def __init__(self):
        """Initialize the activity analyzer."""
        self.use_agent = bool(BEDROCK_AGENT_ID and BEDROCK_AGENT_ALIAS_ID)

    def format_duration(self, seconds: int) -> str:
        """
        Format duration in seconds to human-readable string.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string (e.g., "1h 23m 45s")
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)

    def format_distance(self, meters: float) -> str:
        """
        Format distance in meters to human-readable string.

        Args:
            meters: Distance in meters

        Returns:
            Formatted distance string
        """
        if meters >= 1000:
            km = meters / 1000
            return f"{km:.2f} km"
        else:
            return f"{meters:.0f} m"

    def calculate_heart_rate_zones(self, avg_hr: int, max_hr: int) -> Dict[str, Any]:
        """
        Calculate heart rate zones and training intensity.

        Args:
            avg_hr: Average heart rate
            max_hr: Maximum heart rate

        Returns:
            Heart rate zone analysis
        """
        # Estimate max HR if not provided (220 - age approximation for age 30)
        estimated_max_hr = 190 if max_hr == 0 else max_hr

        # Calculate percentage of max HR
        hr_percentage = (avg_hr / estimated_max_hr) * 100

        # Determine training zone
        if hr_percentage < 60:
            zone = "Zone 1 (Very Light)"
            description = "Recovery and warm-up intensity"
        elif hr_percentage < 70:
            zone = "Zone 2 (Light)"
            description = "Fat burning and aerobic endurance"
        elif hr_percentage < 80:
            zone = "Zone 3 (Moderate)"
            description = "Aerobic capacity building"
        elif hr_percentage < 90:
            zone = "Zone 4 (Hard)"
            description = "Lactate threshold and performance"
        else:
            zone = "Zone 5 (Maximum)"
            description = "Maximum effort and VO2 max"

        return {
            'zone': zone,
            'description': description,
            'percentage_of_max': round(hr_percentage, 1),
            'avg_hr': avg_hr,
            'max_hr': max_hr
        }

    def build_analysis_prompt(self, metrics: Dict[str, Any], activity_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Build comprehensive analysis prompt for AI.

        Args:
            metrics: Current activity metrics
            activity_history: Optional historical activity data

        Returns:
            Formatted prompt string
        """
        activity_type = metrics.get('activity_type', 'UNKNOWN')
        duration = metrics.get('duration_seconds', 0)
        distance = metrics.get('distance_meters', 0)
        calories = metrics.get('calories', 0)

        prompt = f"""Analyze this Garmin fitness activity and provide comprehensive insights:

**Activity Details:**
- Type: {activity_type}
- Duration: {self.format_duration(duration)}
- Distance: {self.format_distance(distance)}
- Calories Burned: {calories} kcal
"""

        # Heart rate analysis
        if 'avg_heart_rate' in metrics:
            avg_hr = metrics['avg_heart_rate']
            max_hr = metrics.get('max_heart_rate', 0)
            hr_zones = self.calculate_heart_rate_zones(avg_hr, max_hr)

            prompt += f"""
**Heart Rate Analysis:**
- Average: {avg_hr} bpm
- Maximum: {max_hr} bpm
- Training Zone: {hr_zones['zone']} ({hr_zones['percentage_of_max']}% of max)
- Zone Description: {hr_zones['description']}
"""

        # Pace and speed
        if 'avg_pace_min_per_km' in metrics:
            pace = metrics['avg_pace_min_per_km']
            prompt += f"\n- Average Pace: {pace:.2f} min/km"

        if 'avg_speed_m_per_s' in metrics:
            speed_kmh = metrics['avg_speed_m_per_s'] * 3.6
            prompt += f"\n- Average Speed: {speed_kmh:.2f} km/h"

        # Elevation
        if 'elevation_gain' in metrics:
            prompt += f"\n- Elevation Gain: {metrics['elevation_gain']} meters"

        # Steps and cadence
        if 'steps' in metrics:
            prompt += f"\n- Steps: {metrics['steps']}"

        if 'avg_cadence' in metrics:
            prompt += f"\n- Average Cadence: {metrics['avg_cadence']} spm/rpm"

        # Training effect
        if 'training_effect' in metrics:
            prompt += f"\n- Training Effect: {metrics['training_effect']}"

        # Historical context
        if activity_history:
            prompt += f"\n\n**Recent Activity History:**\n"
            for idx, hist_activity in enumerate(activity_history[:5], 1):
                hist_metrics = hist_activity.get('metrics', {})
                hist_type = hist_metrics.get('activity_type', 'UNKNOWN')
                hist_duration = self.format_duration(hist_metrics.get('duration_seconds', 0))
                hist_distance = self.format_distance(hist_metrics.get('distance_meters', 0))
                prompt += f"{idx}. {hist_type}: {hist_distance} in {hist_duration}\n"

        prompt += """

**Please provide:**

1. **Performance Assessment:**
   - Overall performance evaluation
   - Strengths observed in this activity
   - Areas for improvement

2. **Health & Fitness Insights:**
   - Cardiovascular fitness indicators
   - Training load and intensity assessment
   - Recovery recommendations

3. **Training Recommendations:**
   - Suggested next workouts
   - Training focus areas
   - Goal-based advice

4. **Comparative Analysis:**
   - How this compares to typical performance for this activity type
   - Progression indicators (if historical data available)

5. **Notable Observations:**
   - Any concerns or red flags
   - Achievements or milestones
   - Data quality issues

Please be specific, actionable, and encouraging in your analysis.
"""

        return prompt

    def invoke_bedrock_agent(self, prompt: str, session_id: str) -> str:
        """
        Invoke Bedrock Agent for analysis.

        Args:
            prompt: Analysis prompt
            session_id: Session identifier

        Returns:
            Agent response text
        """
        logger.info(f"Invoking Bedrock Agent {BEDROCK_AGENT_ID}")

        response = bedrock_agent_runtime.invoke_agent(
            agentId=BEDROCK_AGENT_ID,
            agentAliasId=BEDROCK_AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=prompt
        )

        # Parse streaming response
        agent_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    agent_response += chunk['bytes'].decode('utf-8')

        return agent_response

    def invoke_bedrock_model(self, prompt: str) -> str:
        """
        Invoke Bedrock foundation model directly (fallback).

        Args:
            prompt: Analysis prompt

        Returns:
            Model response text
        """
        logger.info(f"Invoking Bedrock Model {BEDROCK_MODEL_ID}")

        # Format for Claude models
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(body)
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

    def analyze(self, activity_id: str, metrics: Dict[str, Any], activity_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Analyze activity using AI.

        Args:
            activity_id: Activity identifier
            metrics: Activity metrics
            activity_history: Optional historical data

        Returns:
            AI analysis text
        """
        prompt = self.build_analysis_prompt(metrics, activity_history)

        try:
            if self.use_agent:
                return self.invoke_bedrock_agent(prompt, f"garmin-{activity_id}")
            else:
                return self.invoke_bedrock_model(prompt)
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            raise


def get_activity_from_dynamodb(activity_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve activity from DynamoDB.

    Args:
        activity_id: Activity ID

    Returns:
        Activity data or None if not found
    """
    try:
        table = dynamodb.Table(ACTIVITIES_TABLE)
        response = table.get_item(Key={'activity_id': activity_id})
        return response.get('Item')
    except Exception as e:
        logger.error(f"Failed to retrieve activity: {str(e)}")
        return None


def get_user_activity_history(user_token: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get user's recent activity history.

    Args:
        user_token: User identifier
        limit: Maximum number of activities to retrieve

    Returns:
        List of recent activities
    """
    try:
        table = dynamodb.Table(ACTIVITIES_TABLE)
        response = table.query(
            IndexName='user-timestamp-index',
            KeyConditionExpression='user_token = :token',
            ExpressionAttributeValues={':token': user_token},
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Failed to retrieve activity history: {str(e)}")
        return []


def update_activity_with_analysis(activity_id: str, analysis: str) -> None:
    """
    Update activity record with AI analysis.

    Args:
        activity_id: Activity ID
        analysis: AI analysis text
    """
    table = dynamodb.Table(ACTIVITIES_TABLE)

    table.update_item(
        Key={'activity_id': activity_id},
        UpdateExpression='SET ai_analysis = :a, processed = :p, analysis_time = :t, #status = :s',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':a': analysis,
            ':p': True,
            ':t': datetime.utcnow().isoformat(),
            ':s': 'analyzed'
        }
    )

    logger.info(f"Updated activity {activity_id} with AI analysis")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for AI activity analysis.

    This function is triggered by EventBridge when activity data is ready.

    Args:
        event: EventBridge event containing activity data
        context: Lambda context object

    Returns:
        Analysis result
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract event details
        detail = event.get('detail', {})
        activity_id = detail.get('activity_id')
        metrics = detail.get('metrics', {})

        if not activity_id:
            raise ValueError("Missing activity_id in event")

        # Get full activity data from DynamoDB
        activity = get_activity_from_dynamodb(activity_id)
        if not activity:
            raise Exception(f"Activity {activity_id} not found in database")

        # Use metrics from event or from database
        if not metrics:
            metrics = activity.get('metrics', {})

        # Get user's activity history for context
        user_token = activity.get('user_token')
        activity_history = []
        if user_token:
            activity_history = get_user_activity_history(user_token, limit=10)

        # Initialize analyzer and perform analysis
        analyzer = ActivityAnalyzer()
        analysis = analyzer.analyze(activity_id, metrics, activity_history)

        # Store analysis in DynamoDB
        update_activity_with_analysis(activity_id, analysis)

        logger.info(f"Successfully analyzed activity {activity_id}")

        return {
            'statusCode': 200,
            'activity_id': activity_id,
            'analysis_length': len(analysis),
            'analysis': analysis[:500] + '...' if len(analysis) > 500 else analysis
        }

    except Exception as e:
        logger.error(f"Error analyzing activity: {str(e)}", exc_info=True)

        # Update activity status to failed
        if 'activity_id' in locals():
            try:
                table = dynamodb.Table(ACTIVITIES_TABLE)
                table.update_item(
                    Key={'activity_id': activity_id},
                    UpdateExpression='SET #status = :s, error_message = :e',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':s': 'analysis_failed',
                        ':e': str(e)
                    }
                )
            except Exception as update_error:
                logger.error(f"Failed to update error status: {str(update_error)}")

        raise
