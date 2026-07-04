---
name: aws-eventbridge
description: Build event-driven architectures and trigger agentic flows with Amazon EventBridge. Use when creating event rules, routing events to Lambda/Step Functions/Bedrock, building scheduled agent triggers, creating custom event buses, or implementing EventBridge Pipes for streaming data. Triggers on EventBridge, event-driven, event bus, event rule, scheduled events, cron trigger, EventBridge Pipes, event pattern, event routing.
---

# Amazon EventBridge

Build event-driven pipelines that trigger AI agents, orchestrate services, and automate workflows.

## Core Concepts

| Concept | Description |
|---------|------------|
| **Event Bus** | Channel that receives events (default, custom, or partner) |
| **Rule** | Pattern match + target routing |
| **Target** | Where matched events are sent (Lambda, SFN, SQS, Bedrock, etc.) |
| **Pipes** | Point-to-point streaming: source → filter → enrich → target |
| **Scheduler** | Cron/rate-based triggers (replaces CloudWatch Events) |

## Send Custom Events

```python
import boto3
import json
from datetime import datetime

events = boto3.client('events', region_name='us-east-1')

response = events.put_events(
    Entries=[
        {
            'Source': 'myapp.orders',
            'DetailType': 'OrderPlaced',
            'Detail': json.dumps({
                'orderId': 'ord-123',
                'customerId': 'cust-456',
                'amount': 249.99,
                'items': ['laptop', 'mouse'],
                'timestamp': datetime.utcnow().isoformat()
            }),
            'EventBusName': 'my-custom-bus'  # omit for default bus
        }
    ]
)

failed = response.get('FailedEntryCount', 0)
if failed:
    print(f"Failed to send {failed} events")
```

## Create Custom Event Bus + Rules (CDK)

```python
from aws_cdk import (
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as lambda_,
    aws_stepfunctions as sfn,
    Stack
)

class EventDrivenAgentStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Custom bus for AI agent events
        agent_bus = events.EventBus(
            self, 'AgentEventBus',
            event_bus_name='agent-events'
        )

        agent_fn = lambda_.Function(self, 'AgentFn', ...)

        # Route document upload events to Lambda agent
        events.Rule(
            self, 'DocumentUploadRule',
            event_bus=agent_bus,
            event_pattern=events.EventPattern(
                source=['myapp.documents'],
                detail_type=['DocumentUploaded'],
                detail={
                    'fileType': ['pdf', 'docx'],
                    'status': ['PENDING']
                }
            ),
            targets=[targets.LambdaFunction(agent_fn)]
        )

        # Route high-value orders to Step Functions
        state_machine = sfn.StateMachine(self, 'OrderPipeline', ...)

        events.Rule(
            self, 'HighValueOrderRule',
            event_bus=agent_bus,
            event_pattern=events.EventPattern(
                source=['myapp.orders'],
                detail_type=['OrderPlaced'],
                detail={'amount': [{'numeric': ['>', 1000]}]}
            ),
            targets=[targets.SfnStateMachine(state_machine)]
        )
```

## EventBridge Scheduler — Cron and Rate Triggers

```python
import boto3
import json

scheduler = boto3.client('scheduler', region_name='us-east-1')

# Daily report agent at 8 AM UTC
scheduler.create_schedule(
    Name='daily-report-agent',
    GroupName='ai-agents',
    ScheduleExpression='cron(0 8 * * ? *)',
    FlexibleTimeWindow={'Mode': 'OFF'},
    Target={
        'Arn': 'arn:aws:lambda:us-east-1:123:function:report-agent',
        'RoleArn': 'arn:aws:iam::123:role/SchedulerExecutionRole',
        'Input': json.dumps({'reportType': 'daily_summary', 'format': 'email'})
    }
)

# Every 15 minutes health check
scheduler.create_schedule(
    Name='health-monitor-agent',
    GroupName='ai-agents',
    ScheduleExpression='rate(15 minutes)',
    FlexibleTimeWindow={'Mode': 'FLEXIBLE', 'MaximumWindowInMinutes': 5},
    Target={
        'Arn': 'arn:aws:states:us-east-1:123:stateMachine:HealthCheckPipeline',
        'RoleArn': 'arn:aws:iam::123:role/SchedulerExecutionRole',
        'Input': json.dumps({'checkType': 'full_system'})
    }
)

# One-time future trigger (auto-deletes after firing)
scheduler.create_schedule(
    Name='contract-review-agent',
    ScheduleExpression='at(2026-03-15T09:00:00)',
    FlexibleTimeWindow={'Mode': 'OFF'},
    Target={
        'Arn': 'arn:aws:lambda:us-east-1:123:function:contract-agent',
        'RoleArn': 'arn:aws:iam::123:role/SchedulerExecutionRole',
        'Input': json.dumps({'contractId': 'cnt-789', 'action': 'review'})
    },
    ActionAfterCompletion='DELETE'
)
```

## EventBridge Pipes — Streaming Sources to Agents

Connect SQS / DynamoDB Streams / Kinesis directly to targets without polling code.

```python
import boto3
import json

pipes = boto3.client('pipes', region_name='us-east-1')

# SQS → filter → Lambda agent
pipes.create_pipe(
    Name='customer-feedback-to-agent',
    RoleArn='arn:aws:iam::123:role/PipesExecutionRole',
    Source='arn:aws:sqs:us-east-1:123:feedback-queue',
    SourceParameters={
        'SqsQueueParameters': {'BatchSize': 10, 'MaximumBatchingWindowInSeconds': 30},
        'FilterCriteria': {
            'Filters': [
                {'Pattern': json.dumps({'body': {'sentiment': ['NEGATIVE']}})}
            ]
        }
    },
    Enrichment='arn:aws:lambda:us-east-1:123:function:enrich-feedback',  # optional transform
    Target='arn:aws:lambda:us-east-1:123:function:respond-to-feedback',
    TargetParameters={
        'LambdaFunctionParameters': {'InvocationType': 'FIRE_AND_FORGET'}
    }
)

# DynamoDB Stream → Step Functions (react to DB changes)
pipes.create_pipe(
    Name='order-updates-to-pipeline',
    RoleArn='arn:aws:iam::123:role/PipesExecutionRole',
    Source='arn:aws:dynamodb:us-east-1:123:table/Orders/stream/...',
    SourceParameters={
        'DynamoDBStreamParameters': {'StartingPosition': 'LATEST', 'BatchSize': 1},
        'FilterCriteria': {
            'Filters': [
                {'Pattern': json.dumps({
                    'dynamodb': {'NewImage': {'status': {'S': ['SHIPPED']}}}
                })}
            ]
        }
    },
    Target='arn:aws:states:us-east-1:123:stateMachine:ShipmentTracker',
    TargetParameters={
        'StepFunctionStateMachineParameters': {'InvocationType': 'FIRE_AND_FORGET'}
    }
)
```

## Event Pattern Reference

```json
{
  "source": ["myapp.orders", "myapp.returns"],
  "detail-type": ["OrderPlaced"],
  "detail": {
    "amount": [{"numeric": [">", 500, "<=", 5000]}],
    "region": ["us-east-1", "us-west-2"],
    "status": [{"anything-but": "CANCELLED"}],
    "tags": {"priority": ["HIGH"]},
    "metadata": {"exists": true}
  },
  "time": [{"prefix": "2026-"}]
}
```

## Lambda Handler for EventBridge Events

```python
import json
import boto3

def lambda_handler(event: dict, context) -> dict:
    source = event['source']           # e.g. "myapp.orders"
    detail_type = event['detail-type'] # e.g. "OrderPlaced"
    detail = event['detail']           # your custom payload

    if detail_type == 'OrderPlaced':
        return handle_order(detail)
    elif detail_type == 'DocumentUploaded':
        return process_document(detail)

    return {'status': 'unhandled'}


def handle_order(order: dict) -> dict:
    bedrock = boto3.client('bedrock-runtime')
    response = bedrock.converse(
        modelId='anthropic.claude-3-5-haiku-20241022-v1:0',
        messages=[{
            'role': 'user',
            'content': [{'text': f"Suggest upsell for: {json.dumps(order)}"}]
        }]
    )
    suggestion = response['output']['message']['content'][0]['text']
    return {'status': 'ok', 'suggestion': suggestion}
```

## Cross-Account Event Routing

```python
# Allow another account to send events to your bus
events.put_permission(
    EventBusName='my-custom-bus',
    Action='events:PutEvents',
    Principal='987654321098',
    StatementId='AllowCrossAccountPut'
)

# Source account: target cross-account bus ARN directly
events.put_events(
    Entries=[{
        'Source': 'partner.service',
        'DetailType': 'DataReady',
        'Detail': json.dumps({'datasetId': 'ds-001'}),
        'EventBusName': 'arn:aws:events:us-east-1:123456789012:event-bus/my-custom-bus'
    }]
)
```

## Archive and Replay

```python
# Archive all agent events for 90 days
events.create_archive(
    ArchiveName='agent-events-archive',
    EventSourceArn='arn:aws:events:us-east-1:123:event-bus/agent-events',
    RetentionDays=90,
    EventPattern=json.dumps({'source': [{'prefix': 'myapp.'}]})
)

# Replay for debugging / reprocessing
events.start_replay(
    ReplayName='debug-replay-2026-02-28',
    EventSourceArn='arn:aws:events:us-east-1:123:archive/agent-events-archive',
    EventStartTime='2026-02-28T00:00:00Z',
    EventEndTime='2026-02-28T23:59:59Z',
    Destination={'Arn': 'arn:aws:events:us-east-1:123:event-bus/agent-events-replay'}
)
```

## Common Agentic Trigger Patterns

| Trigger | EventBridge Component | Agent Action |
|---------|-----------------------|-------------|
| File uploaded to S3 | S3 → EventBridge → Rule | Analyze / process file |
| DynamoDB record updated | Pipes (DynamoDB Stream) | React to data change |
| Scheduled daily digest | Scheduler (cron) | Generate + send report |
| New SQS message | Pipes (SQS source) | Process customer request |
| Step Functions completed | EventBridge (SFN events) | Trigger downstream agent |
| API call detected | CloudTrail → EventBridge | Security agent alert |
| Cost threshold exceeded | Cost Anomaly Detection | Alert + remediation agent |

## IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["events:PutEvents"],
      "Resource": "arn:aws:events:us-east-1:123:event-bus/agent-events"
    },
    {
      "Effect": "Allow",
      "Action": ["scheduler:CreateSchedule", "scheduler:DeleteSchedule"],
      "Resource": "arn:aws:scheduler:us-east-1:123:schedule/ai-agents/*"
    }
  ]
}
```

## Resources

- **EventBridge docs**: https://docs.aws.amazon.com/eventbridge/
- **EventBridge Pipes**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes.html
- **EventBridge Scheduler**: https://docs.aws.amazon.com/scheduler/latest/UserGuide/
- **Event patterns**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html
- **Schema registry**: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schema.html
