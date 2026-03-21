---
name: aws-lambda
description: Build, deploy, and optimize AWS Lambda functions as agent tool backends. Use when writing Lambda handlers for Bedrock action groups, implementing function URLs, setting up event sources (SQS, EventBridge, API GW, S3), using AWS Lambda Powertools, configuring layers and container images, or testing with SAM CLI. Triggers on Lambda function, Lambda tool, serverless function, Lambda handler, function URL, agent tool backend, Lambda layers, Lambda container, SAM CLI.
---

# AWS Lambda

Build serverless functions as backends for AI agents, automation triggers, and tool implementations.

## Lambda as a Bedrock Agent Tool (Action Group)

This is the primary pattern for agent tool backends:

```python
import json
import boto3
from typing import Any

def lambda_handler(event: dict, context: Any) -> dict:
    """Bedrock agent action group handler."""
    action_group = event.get('actionGroup', '')
    function_name = event.get('function', '')
    parameters = {p['name']: p['value'] for p in event.get('parameters', [])}

    result = dispatch(action_group, function_name, parameters)

    return {
        'response': {
            'actionGroup': action_group,
            'function': function_name,
            'functionResponse': {
                'responseBody': {
                    'TEXT': {'body': json.dumps(result)}
                }
            }
        }
    }


def dispatch(action_group: str, function: str, params: dict) -> dict:
    if function == 'search_products':
        return search_products(params['query'], int(params.get('limit', 10)))
    elif function == 'get_order_status':
        return get_order_status(params['order_id'])
    elif function == 'create_ticket':
        return create_ticket(params['title'], params['description'], params.get('priority', 'MEDIUM'))
    return {'error': f'Unknown function: {function}'}


def search_products(query: str, limit: int) -> dict:
    # Your business logic here
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Products')
    # ... query table
    return {'results': [], 'count': 0}


def get_order_status(order_id: str) -> dict:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Orders')
    response = table.get_item(Key={'orderId': order_id})
    item = response.get('Item')
    if not item:
        return {'error': 'Order not found'}
    return {'orderId': order_id, 'status': item['status'], 'updatedAt': item['updatedAt']}


def create_ticket(title: str, description: str, priority: str) -> dict:
    # Create support ticket, JIRA issue, etc.
    return {'ticketId': 'TKT-001', 'status': 'created', 'priority': priority}
```

## Function URL — HTTP Endpoint for Agents

Expose Lambda directly as an HTTPS endpoint (no API Gateway needed):

```python
# CDK: add Function URL
from aws_cdk import aws_lambda as lambda_

fn = lambda_.Function(self, 'AgentTool',
    runtime=lambda_.Runtime.PYTHON_3_12,
    handler='handler.lambda_handler',
    code=lambda_.Code.from_asset('src/'),
    environment={'TABLE_NAME': 'Products'}
)

url = fn.add_function_url(
    auth_type=lambda_.FunctionUrlAuthType.AWS_IAM,  # or NONE for public
    cors=lambda_.FunctionUrlCorsOptions(
        allowed_origins=['*'],
        allowed_methods=[lambda_.HttpMethod.POST]
    )
)
```

```python
# boto3: invoke via Function URL
import urllib.request
import json

def call_agent_tool(function_url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        function_url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
```

## Event Sources

### SQS Trigger

```python
def lambda_handler(event: dict, context) -> dict:
    for record in event['Records']:
        body = json.loads(record['body'])
        process_message(body)
        # Lambda auto-deletes messages on success
    return {'statusCode': 200}
```

### API Gateway (REST or HTTP API)

```python
def lambda_handler(event: dict, context) -> dict:
    method = event['httpMethod']
    path = event['path']
    body = json.loads(event.get('body') or '{}')
    query = event.get('queryStringParameters') or {}

    if method == 'POST' and path == '/analyze':
        result = analyze(body)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }

    return {'statusCode': 404, 'body': '{"error": "Not found"}'}
```

### EventBridge Trigger

```python
def lambda_handler(event: dict, context) -> dict:
    # event['source'], event['detail-type'], event['detail']
    detail = event['detail']
    process_event(event['detail-type'], detail)
    return {'status': 'processed'}
```

### S3 Trigger

```python
import urllib.parse

def lambda_handler(event: dict, context) -> dict:
    s3 = boto3.client('s3')
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        process_s3_object(s3, bucket, key)
    return {'status': 'ok'}
```

## AWS Lambda Powertools

Essential utilities for production Lambda functions:

```python
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validate
from aws_lambda_powertools.event_handler import APIGatewayRestResolver

logger = Logger(service='agent-tool')
tracer = Tracer(service='agent-tool')
metrics = Metrics(namespace='AgentTools', service='agent-tool')
app = APIGatewayRestResolver()

@app.post('/analyze')
@tracer.capture_method
def analyze_document():
    body = app.current_event.json_body
    logger.info("Analyzing document", document_id=body.get('id'))
    result = run_analysis(body)
    metrics.add_metric(name='AnalysisCount', unit=MetricUnit.Count, value=1)
    return {'result': result}

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

Install:
```bash
pip install aws-lambda-powertools[all]
```

## Response Streaming

For long-running AI responses, stream back to the caller:

```python
import json

def lambda_handler(event: dict, context):
    """Requires RESPONSE_STREAM InvocationType + Function URL with streaming."""
    def generate():
        bedrock = boto3.client('bedrock-runtime')
        response = bedrock.converse_stream(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            messages=[{'role': 'user', 'content': [{'text': event['prompt']}]}]
        )
        for chunk in response['stream']:
            if 'contentBlockDelta' in chunk:
                text = chunk['contentBlockDelta']['delta'].get('text', '')
                if text:
                    yield text.encode('utf-8')

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/plain'},
        'body': generate()
    }
```

## Lambda Layers — Shared Dependencies

```python
# CDK: create and attach a layer
from aws_cdk import aws_lambda as lambda_

powertools_layer = lambda_.LayerVersion.from_layer_version_arn(
    self, 'PowertoolsLayer',
    # Latest ARN from: https://docs.powertools.aws.dev/lambda/python/latest/
    f'arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV3-python312-x86_64:8'
)

fn = lambda_.Function(self, 'AgentFn',
    runtime=lambda_.Runtime.PYTHON_3_12,
    handler='handler.lambda_handler',
    code=lambda_.Code.from_asset('src/'),
    layers=[powertools_layer]
)
```

## Container Image Lambda

For large dependencies (ML models, large SDKs):

```dockerfile
# Dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY src/ ${LAMBDA_TASK_ROOT}/

CMD ["handler.lambda_handler"]
```

```python
# CDK: deploy container Lambda
fn = lambda_.DockerImageFunction(
    self, 'AgentContainerFn',
    code=lambda_.DockerImageCode.from_image_asset('./'),
    memory_size=3008,
    timeout=Duration.minutes(5)
)
```

## Environment Variables and Secrets

```python
import os
import boto3
import json

# Simple env var (non-sensitive)
TABLE_NAME = os.environ['TABLE_NAME']
MODEL_ID = os.environ.get('MODEL_ID', 'anthropic.claude-3-5-haiku-20241022-v1:0')

# Secrets Manager (sensitive values — load once at cold start)
_secret_cache = {}

def get_secret(secret_name: str) -> dict:
    if secret_name not in _secret_cache:
        sm = boto3.client('secretsmanager')
        response = sm.get_secret_value(SecretId=secret_name)
        _secret_cache[secret_name] = json.loads(response['SecretString'])
    return _secret_cache[secret_name]

# SSM Parameter Store (non-secret config)
def get_parameter(name: str) -> str:
    ssm = boto3.client('ssm')
    return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']
```

## Concurrency Configuration

```python
# CDK: control concurrency
fn = lambda_.Function(self, 'AgentFn', ...)

# Reserved: cap total concurrent executions
fn.add_reserved_concurrency(reserved_concurrent_executions=50)

# Provisioned: eliminate cold starts for latency-sensitive agents
alias = fn.add_alias('production')
alias.add_provisioned_concurrency(provisioned_concurrent_executions=5)
```

## IAM Execution Role (Least Privilege for AI Agents)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agent-runtime:Retrieve",
        "bedrock-agent-runtime:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:us-east-1:123:knowledge-base/ABCDEF"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Query"],
      "Resource": "arn:aws:dynamodb:us-east-1:123:table/AgentData"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:us-east-1:123:log-group:/aws/lambda/agent-tool:*"
    },
    {
      "Effect": "Allow",
      "Action": ["xray:PutTraceSegments", "xray:PutTelemetryRecords"],
      "Resource": "*"
    }
  ]
}
```

## Local Testing with SAM CLI

```bash
# Install SAM CLI
pip install aws-sam-cli

# Init a Lambda project
sam init --runtime python3.12 --name my-agent-tool

# Invoke locally (uses Docker)
sam local invoke AgentFn --event events/test-event.json

# Start local API Gateway
sam local start-api --port 3000

# Test EventBridge event locally
sam local invoke AgentFn --event events/eventbridge-event.json

# Build and deploy
sam build
sam deploy --guided
```

```json
// events/bedrock-action-group.json
{
  "actionGroup": "ProductTools",
  "function": "search_products",
  "parameters": [
    {"name": "query", "value": "laptop"},
    {"name": "limit", "value": "5"}
  ]
}
```

## Resources

- **Lambda docs**: https://docs.aws.amazon.com/lambda/
- **Lambda Powertools**: https://docs.powertools.aws.dev/lambda/python/latest/
- **Bedrock action groups**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-action-create.html
- **Function URLs**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html
- **SAM CLI**: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/
- **Container images**: https://docs.aws.amazon.com/lambda/latest/dg/images-create.html
