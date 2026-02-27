"""
Garmin OAuth Handler Lambda Function

This function handles OAuth 1.0a authentication flow with Garmin Health API.
It manages the three-legged OAuth process for user authorization.

Environment Variables:
    TOKENS_TABLE_NAME: DynamoDB table storing user OAuth tokens
    GARMIN_CREDENTIALS_SECRET: AWS Secrets Manager secret name
    CALLBACK_URL: OAuth callback URL (API Gateway endpoint)
"""

import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import requests
from requests_oauthlib import OAuth1Session
import urllib.parse

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')

# Environment variables
TOKENS_TABLE = os.environ.get('TOKENS_TABLE_NAME', 'garmin-user-tokens')
GARMIN_CREDENTIALS_SECRET = os.environ.get('GARMIN_CREDENTIALS_SECRET', 'garmin-api-credentials')
CALLBACK_URL = os.environ.get('CALLBACK_URL', 'https://your-api-gateway-url/oauth/callback')

# Garmin OAuth endpoints
REQUEST_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/request_token"
AUTHORIZATION_URL = "https://connect.garmin.com/oauthConfirm"
ACCESS_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/access_token"

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GarminOAuthError(Exception):
    """Custom exception for OAuth errors."""
    pass


def get_garmin_credentials() -> Dict[str, str]:
    """
    Retrieve Garmin API credentials from AWS Secrets Manager.

    Returns:
        Dictionary with consumer_key and consumer_secret
    """
    try:
        response = secrets_client.get_secret_value(SecretId=GARMIN_CREDENTIALS_SECRET)
        secret_string = response['SecretString']
        credentials = json.loads(secret_string)

        if 'consumer_key' not in credentials or 'consumer_secret' not in credentials:
            raise GarminOAuthError("Invalid credentials format in Secrets Manager")

        return credentials

    except Exception as e:
        logger.error(f"Failed to retrieve Garmin credentials: {str(e)}")
        raise


def initiate_oauth_flow(user_id: str) -> Dict[str, str]:
    """
    Initiate OAuth flow by requesting a request token.

    Args:
        user_id: Identifier for the user initiating OAuth

    Returns:
        Dictionary with authorization_url and request_token

    Raises:
        GarminOAuthError: If OAuth flow initiation fails
    """
    credentials = get_garmin_credentials()

    # Create OAuth1Session
    oauth = OAuth1Session(
        credentials['consumer_key'],
        client_secret=credentials['consumer_secret'],
        callback_uri=CALLBACK_URL
    )

    try:
        # Request token
        response = oauth.fetch_request_token(REQUEST_TOKEN_URL)

        request_token = response.get('oauth_token')
        request_token_secret = response.get('oauth_token_secret')

        if not request_token or not request_token_secret:
            raise GarminOAuthError("Failed to obtain request token")

        # Store request token in DynamoDB temporarily
        table = dynamodb.Table(TOKENS_TABLE)
        table.put_item(
            Item={
                'user_token': f"request_{user_id}",
                'request_token': request_token,
                'request_token_secret': request_token_secret,
                'user_id': user_id,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'ttl': int(datetime.utcnow().timestamp()) + 3600  # Expire in 1 hour
            }
        )

        # Build authorization URL
        authorization_url = f"{AUTHORIZATION_URL}?oauth_token={request_token}"

        logger.info(f"OAuth flow initiated for user {user_id}")

        return {
            'authorization_url': authorization_url,
            'request_token': request_token,
            'user_id': user_id
        }

    except Exception as e:
        logger.error(f"OAuth initiation failed: {str(e)}")
        raise GarminOAuthError(f"Failed to initiate OAuth: {str(e)}")


def complete_oauth_flow(oauth_token: str, oauth_verifier: str) -> Dict[str, str]:
    """
    Complete OAuth flow by exchanging verifier for access token.

    Args:
        oauth_token: OAuth token from callback
        oauth_verifier: OAuth verifier from callback

    Returns:
        Dictionary with access_token and user information

    Raises:
        GarminOAuthError: If OAuth completion fails
    """
    credentials = get_garmin_credentials()

    # Retrieve request token from DynamoDB
    table = dynamodb.Table(TOKENS_TABLE)

    try:
        # Find the request token record
        response = table.scan(
            FilterExpression='request_token = :token',
            ExpressionAttributeValues={':token': oauth_token}
        )

        items = response.get('Items', [])
        if not items:
            raise GarminOAuthError("Request token not found or expired")

        request_data = items[0]
        request_token_secret = request_data['request_token_secret']
        user_id = request_data['user_id']

        # Create OAuth1Session with request token
        oauth = OAuth1Session(
            credentials['consumer_key'],
            client_secret=credentials['consumer_secret'],
            resource_owner_key=oauth_token,
            resource_owner_secret=request_token_secret,
            verifier=oauth_verifier
        )

        # Exchange for access token
        access_response = oauth.fetch_access_token(ACCESS_TOKEN_URL)

        access_token = access_response.get('oauth_token')
        access_token_secret = access_response.get('oauth_token_secret')

        if not access_token or not access_token_secret:
            raise GarminOAuthError("Failed to obtain access token")

        # Generate user access token (this is what Garmin uses in webhooks)
        user_access_token = f"user_{user_id}_{access_token[:10]}"

        # Store access token in DynamoDB
        table.put_item(
            Item={
                'user_token': user_access_token,
                'access_token': access_token,
                'access_token_secret': access_token_secret,
                'user_id': user_id,
                'status': 'active',
                'created_at': datetime.utcnow().isoformat(),
                'authorized_at': datetime.utcnow().isoformat()
            }
        )

        # Delete temporary request token
        table.delete_item(Key={'user_token': f"request_{user_id}"})

        logger.info(f"OAuth flow completed for user {user_id}")

        return {
            'user_access_token': user_access_token,
            'user_id': user_id,
            'status': 'authorized'
        }

    except Exception as e:
        logger.error(f"OAuth completion failed: {str(e)}")
        raise GarminOAuthError(f"Failed to complete OAuth: {str(e)}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for OAuth flow.

    Handles two endpoints:
    1. /oauth/initiate - Start OAuth flow
    2. /oauth/callback - Complete OAuth flow

    Args:
        event: API Gateway event
        context: Lambda context object

    Returns:
        API Gateway response
    """
    logger.info(f"Received OAuth event: {json.dumps(event)}")

    try:
        path = event.get('path', '')
        http_method = event.get('httpMethod', 'GET')

        # Initiate OAuth flow
        if path.endswith('/oauth/initiate') and http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            user_id = body.get('user_id')

            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'user_id is required'})
                }

            result = initiate_oauth_flow(user_id)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'authorization_url': result['authorization_url'],
                    'message': 'Redirect user to authorization_url to complete OAuth'
                })
            }

        # OAuth callback
        elif path.endswith('/oauth/callback') and http_method == 'GET':
            query_params = event.get('queryStringParameters', {})
            oauth_token = query_params.get('oauth_token')
            oauth_verifier = query_params.get('oauth_verifier')

            if not oauth_token or not oauth_verifier:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'text/html'},
                    'body': '<html><body><h1>OAuth Error</h1><p>Missing oauth_token or oauth_verifier</p></body></html>'
                }

            result = complete_oauth_flow(oauth_token, oauth_verifier)

            # Return success page
            success_html = f"""
            <html>
            <head>
                <title>Garmin Authorization Successful</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .success {{ color: green; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="success">✓ Authorization Successful</h1>
                    <p>Your Garmin account has been successfully connected!</p>
                    <p>You can now close this window.</p>
                    <hr>
                    <p><small>User ID: {result['user_id']}</small></p>
                </div>
            </body>
            </html>
            """

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': success_html
            }

        # Unknown endpoint
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Not found'})
            }

    except GarminOAuthError as e:
        logger.error(f"OAuth error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }

    except Exception as e:
        logger.error(f"Unexpected error in OAuth handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }


def deauthorize_user(user_token: str) -> None:
    """
    Deauthorize a user and remove their tokens.

    Args:
        user_token: User's access token to revoke
    """
    try:
        table = dynamodb.Table(TOKENS_TABLE)
        table.delete_item(Key={'user_token': user_token})
        logger.info(f"Deauthorized user token {user_token[:10]}...")

    except Exception as e:
        logger.error(f"Failed to deauthorize user: {str(e)}")
        raise
