---
name: aws-step-functions
description: Orchestrate multi-step agentic and automation workflows with AWS Step Functions. Use when designing state machines, building human-in-the-loop approval flows, parallel agent execution, retry logic, or long-running agentic pipelines. Triggers on Step Functions, state machine, workflow orchestration, AWS workflow, agentic orchestration, Express Workflow, Standard Workflow, ASL.
---

# AWS Step Functions

Orchestrate complex agentic workflows with durable, visual state machines.

## Workflow Types

| Type | Duration | Pricing | Use Case |
|------|----------|---------|---------|
| **Standard** | Up to 1 year | Per state transition | Long-running agents, human approval, durable jobs |
| **Express** | Up to 5 min | Per execution + duration | High-throughput, event processing, short pipelines |

## Quick Start — Define a State Machine (CDK)

```python
from aws_cdk import (
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_lambda as lambda_,
    aws_bedrock as bedrock,
    Stack
)

class AgentOrchestrationStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda tools
        extract_fn = lambda_.Function(self, 'ExtractFn', ...)
        classify_fn = lambda_.Function(self, 'ClassifyFn', ...)
        respond_fn = lambda_.Function(self, 'RespondFn', ...)

        # Step 1: Extract
        extract = tasks.LambdaInvoke(
            self, 'ExtractData',
            lambda_function=extract_fn,
            output_path='$.Payload'
        )

        # Step 2: Classify (parallel paths)
        classify_positive = tasks.LambdaInvoke(self, 'ClassifyPositive', lambda_function=classify_fn)
        classify_negative = tasks.LambdaInvoke(self, 'ClassifyNegative', lambda_function=classify_fn)

        parallel = sfn.Parallel(self, 'ParallelClassify')
        parallel.branch(classify_positive)
        parallel.branch(classify_negative)

        # Step 3: Choice gate
        is_positive = sfn.Choice(self, 'IsPositive') \
            .when(
                sfn.Condition.string_equals('$.sentiment', 'POSITIVE'),
                tasks.LambdaInvoke(self, 'RespondPositive', lambda_function=respond_fn)
            ) \
            .otherwise(
                tasks.LambdaInvoke(self, 'RespondNegative', lambda_function=respond_fn)
            )

        # Chain
        definition = extract.next(parallel).next(is_positive)

        sfn.StateMachine(
            self, 'AgentOrchestration',
            definition=definition,
            state_machine_type=sfn.StateMachineType.STANDARD
        )
```

## Amazon States Language (ASL) — JSON Definition

```json
{
  "Comment": "Agentic pipeline: extract → classify → respond",
  "StartAt": "ExtractData",
  "States": {
    "ExtractData": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:123:function:extract",
        "Payload.$": "$"
      },
      "ResultPath": "$.extracted",
      "Next": "ClassifyIntent"
    },
    "ClassifyIntent": {
      "Type": "Task",
      "Resource": "arn:aws:states:::bedrock:invokeModel",
      "Parameters": {
        "ModelId": "anthropic.claude-3-5-haiku-20241022-v1:0",
        "Body": {
          "anthropic_version": "bedrock-2023-05-31",
          "max_tokens": 64,
          "messages": [
            {
              "role": "user",
              "content.$": "States.Format('Classify intent: {}', $.extracted.text)"
            }
          ]
        }
      },
      "ResultPath": "$.classification",
      "Next": "RouteByIntent"
    },
    "RouteByIntent": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.classification.content[0].text",
          "StringMatches": "*complaint*",
          "Next": "EscalateToHuman"
        },
        {
          "Variable": "$.classification.content[0].text",
          "StringMatches": "*order*",
          "Next": "HandleOrder"
        }
      ],
      "Default": "GeneralResponse"
    },
    "EscalateToHuman": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
      "Parameters": {
        "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123/approvals",
        "MessageBody": {
          "taskToken.$": "$$.Task.Token",
          "input.$": "$"
        }
      },
      "HeartbeatSeconds": 3600,
      "Next": "SendResponse"
    },
    "HandleOrder": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:123:function:handle-order",
        "Payload.$": "$"
      },
      "Retry": [
        {
          "ErrorEquals": ["Lambda.ServiceException", "Lambda.TooManyRequestsException"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "HandleError",
          "ResultPath": "$.error"
        }
      ],
      "Next": "SendResponse"
    },
    "GeneralResponse": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:123:function:respond",
        "Payload.$": "$"
      },
      "End": true
    },
    "SendResponse": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:123:function:send-response",
        "Payload.$": "$"
      },
      "End": true
    },
    "HandleError": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:us-east-1:123:function:error-handler",
        "Payload.$": "$"
      },
      "End": true
    }
  }
}
```

## Bedrock Direct Integration (no Lambda)

```json
{
  "InvokeBedrockModel": {
    "Type": "Task",
    "Resource": "arn:aws:states:::bedrock:invokeModel",
    "Parameters": {
      "ModelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
      "Body": {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": "You are a helpful assistant.",
        "messages": [
          {
            "role": "user",
            "content.$": "$.userInput"
          }
        ]
      },
      "ContentType": "application/json",
      "Accept": "application/json"
    },
    "ResultSelector": {
      "responseText.$": "$.Body.content[0].text"
    },
    "ResultPath": "$.bedrockResponse",
    "Next": "ProcessResponse"
  }
}
```

## Human-in-the-Loop Pattern

```python
import boto3
import json

sfn_client = boto3.client('stepfunctions')

# Start execution
execution = sfn_client.start_execution(
    stateMachineArn='arn:aws:states:us-east-1:123:stateMachine:AgentPipeline',
    input=json.dumps({'userId': 'u-123', 'request': 'Refund $500'})
)

# --- In your approval Lambda or SQS consumer ---
def process_approval(event, context):
    task_token = event['taskToken']
    approved = human_review_ui(event['input'])  # Your UI logic

    if approved:
        sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps({'approved': True, 'reviewer': 'manager@corp.com'})
        )
    else:
        sfn_client.send_task_failure(
            taskToken=task_token,
            error='ApprovalDenied',
            cause='Manager rejected the refund request'
        )
```

## Map State — Process Items in Parallel

```json
{
  "ProcessDocuments": {
    "Type": "Map",
    "ItemsPath": "$.documents",
    "MaxConcurrency": 10,
    "ItemProcessor": {
      "ProcessorConfig": {"Mode": "INLINE"},
      "StartAt": "AnalyzeDoc",
      "States": {
        "AnalyzeDoc": {
          "Type": "Task",
          "Resource": "arn:aws:states:::bedrock:invokeModel",
          "Parameters": {
            "ModelId": "anthropic.claude-3-5-haiku-20241022-v1:0",
            "Body": {
              "anthropic_version": "bedrock-2023-05-31",
              "max_tokens": 256,
              "messages": [{"role": "user", "content.$": "$.text"}]
            }
          },
          "End": true
        }
      }
    },
    "ResultPath": "$.analysisResults",
    "Next": "AggregateResults"
  }
}
```

## Invoke Step Functions via boto3

```python
import boto3
import json

sfn = boto3.client('stepfunctions', region_name='us-east-1')

# Start execution
response = sfn.start_execution(
    stateMachineArn='arn:aws:states:us-east-1:123456789:stateMachine:MyAgent',
    name='exec-20260228-001',  # unique per execution
    input=json.dumps({'query': 'Analyze Q4 sales data', 'userId': 'u-456'})
)
execution_arn = response['executionArn']

# Poll for completion (for Express, use sync)
result = sfn.start_sync_execution(  # Express only
    stateMachineArn='arn:aws:states:us-east-1:123:stateMachine:FastAgent',
    input=json.dumps({'task': 'classify'})
)
print(json.loads(result['output']))

# For Standard: describe execution
status = sfn.describe_execution(executionArn=execution_arn)
print(status['status'])  # RUNNING | SUCCEEDED | FAILED | ABORTED | TIMED_OUT
```

## Key Patterns for Agentic Flows

| Pattern | ASL Type | When to Use |
|---------|----------|------------|
| Sequential steps | `Task` chain | Linear pipeline |
| Branch on output | `Choice` | Route by intent/classification |
| Parallel agents | `Parallel` | Independent sub-tasks |
| Batch processing | `Map` | Process lists of items |
| Human approval | `Task` + `.waitForTaskToken` | Review gates |
| Retry transient errors | `Retry` config | API throttling, Lambda timeouts |
| Catch & fallback | `Catch` config | Graceful degradation |
| Wait for event | `Task` + `.waitForTaskToken` | Async webhooks |

## IAM Permissions for Step Functions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["lambda:InvokeFunction"],
      "Resource": "arn:aws:lambda:us-east-1:123:function:*"
    },
    {
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage"],
      "Resource": "arn:aws:sqs:us-east-1:123:approvals"
    },
    {
      "Effect": "Allow",
      "Action": ["xray:PutTraceSegments", "xray:GetSamplingRules"],
      "Resource": "*"
    }
  ]
}
```

## Resources

- **Step Functions docs**: https://docs.aws.amazon.com/step-functions/
- **SDK integrations**: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-service-integrations.html
- **Bedrock integration**: https://docs.aws.amazon.com/step-functions/latest/dg/connect-bedrock.html
- **ASL reference**: https://states-language.net/spec.html
- **Workflow Studio**: Use the AWS Console visual editor for flow design
