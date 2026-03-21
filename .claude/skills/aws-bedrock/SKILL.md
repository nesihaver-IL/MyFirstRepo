---
name: aws-bedrock
description: Work with Amazon Bedrock foundational models, Knowledge Bases (RAG), Bedrock Flows, Guardrails, and Prompt Management. Use when invoking Bedrock models, building RAG pipelines, designing visual agentic flows, applying content filters, or managing prompt templates. Triggers on Bedrock models, converse API, Knowledge Base, Bedrock Flows, Guardrails, Prompt Management, model invocation, RAG on Bedrock.
---

# Amazon Bedrock

Full reference for Amazon Bedrock: model invocation, Knowledge Bases, Flows, Guardrails, and Prompt Management.

## Model Invocation — Converse API (recommended)

```python
import boto3

client = boto3.client('bedrock-runtime', region_name='us-east-1')

response = client.converse(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[
        {"role": "user", "content": [{"text": "Summarize the key risks in this contract."}]}
    ],
    system=[{"text": "You are a legal analyst. Be concise and precise."}],
    inferenceConfig={
        "maxTokens": 1024,
        "temperature": 0.3
    }
)

print(response['output']['message']['content'][0]['text'])
```

### Converse with Tool Use

```python
tools = [
    {
        "toolSpec": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a ticker symbol.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"}
                    },
                    "required": ["ticker"]
                }
            }
        }
    }
]

response = client.converse(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[{"role": "user", "content": [{"text": "What is the current price of AMZN?"}]}],
    toolConfig={"tools": tools}
)

# Handle tool use in agentic loop
def run_agentic_loop(user_message: str) -> str:
    messages = [{"role": "user", "content": [{"text": user_message}]}]

    while True:
        response = client.converse(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            messages=messages,
            toolConfig={"tools": tools}
        )
        stop_reason = response['stopReason']
        assistant_message = response['output']['message']
        messages.append(assistant_message)

        if stop_reason == 'end_turn':
            return assistant_message['content'][0]['text']

        if stop_reason == 'tool_use':
            tool_results = []
            for block in assistant_message['content']:
                if block.get('type') == 'toolUse' or 'toolUse' in block:
                    tool_use = block.get('toolUse', block)
                    result = execute_tool(tool_use['name'], tool_use['input'])
                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_use['toolUseId'],
                            "content": [{"text": str(result)}]
                        }
                    })
            messages.append({"role": "user", "content": tool_results})
```

### Streaming Responses

```python
response = client.converse_stream(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[{"role": "user", "content": [{"text": "Write a product description."}]}]
)

for event in response['stream']:
    if 'contentBlockDelta' in event:
        print(event['contentBlockDelta']['delta'].get('text', ''), end='', flush=True)
```

## Available Models

| Model ID | Use Case |
|----------|---------|
| `anthropic.claude-3-5-sonnet-20241022-v2:0` | Best reasoning, complex tasks |
| `anthropic.claude-3-5-haiku-20241022-v1:0` | Fast, cost-efficient tasks |
| `anthropic.claude-3-opus-20240229-v1:0` | Long documents, analysis |
| `amazon.nova-pro-v1:0` | AWS-native multimodal |
| `amazon.nova-lite-v1:0` | Low-latency, high volume |
| `amazon.titan-embed-text-v2:0` | Text embeddings for RAG |
| `cohere.embed-english-v3` | Cohere embeddings |
| `meta.llama3-2-90b-instruct-v1:0` | Open-source Llama 3 |

## Knowledge Bases (RAG)

### Create Knowledge Base

```python
bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')

# Create KB backed by OpenSearch Serverless
kb = bedrock_agent.create_knowledge_base(
    name='product-catalog-kb',
    description='Product catalog for customer support RAG',
    roleArn='arn:aws:iam::123456789:role/AmazonBedrockExecutionRoleForKnowledgeBase',
    knowledgeBaseConfiguration={
        'type': 'VECTOR',
        'vectorKnowledgeBaseConfiguration': {
            'embeddingModelArn': 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0'
        }
    },
    storageConfiguration={
        'type': 'OPENSEARCH_SERVERLESS',
        'opensearchServerlessConfiguration': {
            'collectionArn': 'arn:aws:aoss:us-east-1:123456789:collection/my-collection',
            'vectorIndexName': 'product-catalog-index',
            'fieldMapping': {
                'vectorField': 'embedding',
                'textField': 'text',
                'metadataField': 'metadata'
            }
        }
    }
)
```

### Retrieve and Generate (RAG)

```python
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = bedrock_agent_runtime.retrieve_and_generate(
    input={'text': 'What is the return policy for electronics?'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'ABCDEF1234',
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0',
            'retrievalConfiguration': {
                'vectorSearchConfiguration': {
                    'numberOfResults': 5,
                    'overrideSearchType': 'HYBRID'  # SEMANTIC or HYBRID
                }
            },
            'generationConfiguration': {
                'inferenceConfig': {
                    'textInferenceConfig': {'maxTokens': 512, 'temperature': 0.1}
                }
            }
        }
    }
)

print(response['output']['text'])
print("Sources:", [c['retrievedReferences'] for c in response.get('citations', [])])
```

### Pure Retrieval (no generation)

```python
response = bedrock_agent_runtime.retrieve(
    knowledgeBaseId='ABCDEF1234',
    retrievalQuery={'text': 'return policy'},
    retrievalConfiguration={
        'vectorSearchConfiguration': {
            'numberOfResults': 10,
            'filter': {
                'equals': {'key': 'category', 'value': 'electronics'}
            }
        }
    }
)

for result in response['retrievalResults']:
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['content']['text'][:200]}")
    print(f"Source: {result['location']}")
```

### Ingest Documents

```python
# Ingest from S3
bedrock_agent.start_ingestion_job(
    knowledgeBaseId='ABCDEF1234',
    dataSourceId='DATA_SOURCE_ID'
)

# Direct ingestion (no S3 needed)
bedrock_agent_runtime.ingest_knowledge_base_documents(
    knowledgeBaseId='ABCDEF1234',
    dataSourceId='DIRECT_UPLOAD_SOURCE_ID',
    documents=[
        {
            'content': {
                'dataSourceType': 'CUSTOM',
                'custom': {
                    'customDocumentIdentifier': {'id': 'doc-001'},
                    'sourceType': 'IN_LINE',
                    'inlineContent': {
                        'type': 'TEXT',
                        'textContent': {'data': 'Your document text here...'}
                    }
                }
            }
        }
    ]
)
```

## Bedrock Flows

Visual no-code/low-code agentic workflow builder.

```python
# Create a flow
flow = bedrock_agent.create_flow(
    name='summarization-flow',
    description='Summarize documents with conditional routing',
    roleArn='arn:aws:iam::123456789:role/AmazonBedrockExecutionRoleForFlows',
    definition={
        'nodes': [
            {
                'name': 'Input',
                'type': 'Input',
                'outputs': [{'name': 'document', 'type': 'String'}]
            },
            {
                'name': 'SummarizePrompt',
                'type': 'Prompt',
                'configuration': {
                    'prompt': {
                        'sourceConfiguration': {
                            'inline': {
                                'modelId': 'anthropic.claude-3-5-haiku-20241022-v1:0',
                                'templateType': 'TEXT',
                                'templateConfiguration': {
                                    'text': {
                                        'text': 'Summarize this: {{document}}',
                                        'inputVariables': [{'name': 'document'}]
                                    }
                                },
                                'inferenceConfiguration': {
                                    'text': {'maxTokens': 256, 'temperature': 0.2}
                                }
                            }
                        }
                    }
                },
                'inputs': [{'name': 'document', 'type': 'String', 'expression': '$.data'}],
                'outputs': [{'name': 'modelCompletion', 'type': 'String'}]
            },
            {
                'name': 'Output',
                'type': 'Output',
                'inputs': [{'name': 'document', 'type': 'String', 'expression': '$.data'}]
            }
        ],
        'connections': [
            {
                'name': 'input-to-prompt',
                'source': 'Input', 'target': 'SummarizePrompt',
                'type': 'Data',
                'configuration': {
                    'data': {'sourceOutput': 'document', 'targetInput': 'document'}
                }
            },
            {
                'name': 'prompt-to-output',
                'source': 'SummarizePrompt', 'target': 'Output',
                'type': 'Data',
                'configuration': {
                    'data': {'sourceOutput': 'modelCompletion', 'targetInput': 'document'}
                }
            }
        ]
    }
)

# Invoke flow
bedrock_agent_runtime.invoke_flow(
    flowIdentifier=flow['flow']['id'],
    flowAliasIdentifier='TSTALIASID',
    inputs=[{'content': {'document': 'Long document text...'}, 'nodeName': 'Input', 'nodeOutputName': 'document'}]
)
```

## Guardrails

Content filtering and safety controls.

```python
# Create guardrail
guardrail = bedrock_agent.create_guardrail(
    name='enterprise-guardrail',
    description='Block PII, competitor mentions, and harmful content',
    contentPolicyConfig={
        'filtersConfig': [
            {'type': 'SEXUAL', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
            {'type': 'VIOLENCE', 'inputStrength': 'MEDIUM', 'outputStrength': 'HIGH'},
            {'type': 'HATE', 'inputStrength': 'HIGH', 'outputStrength': 'HIGH'},
            {'type': 'INSULTS', 'inputStrength': 'LOW', 'outputStrength': 'MEDIUM'}
        ]
    },
    sensitiveInformationPolicyConfig={
        'piiEntitiesConfig': [
            {'type': 'EMAIL', 'action': 'ANONYMIZE'},
            {'type': 'PHONE', 'action': 'ANONYMIZE'},
            {'type': 'US_SOCIAL_SECURITY_NUMBER', 'action': 'BLOCK'}
        ]
    },
    wordPolicyConfig={
        'wordsConfig': [
            {'text': 'competitor-name'},
            {'text': 'confidential-project'}
        ],
        'managedWordListsConfig': [{'type': 'PROFANITY'}]
    },
    blockedInputMessaging='I cannot process this request.',
    blockedOutputsMessaging='I cannot provide that information.'
)

# Apply guardrail to model call
response = client.converse(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[{"role": "user", "content": [{"text": user_input}]}],
    guardrailConfig={
        'guardrailIdentifier': guardrail['guardrailId'],
        'guardrailVersion': 'DRAFT',
        'trace': 'enabled'
    }
)
```

## Prompt Management

Version-controlled, reusable prompt templates.

```python
# Create a prompt template
prompt = bedrock_agent.create_prompt(
    name='customer-support-template',
    description='Standard customer support response prompt',
    variants=[
        {
            'name': 'default',
            'modelId': 'anthropic.claude-3-5-haiku-20241022-v1:0',
            'templateType': 'TEXT',
            'templateConfiguration': {
                'text': {
                    'text': (
                        'You are a customer support agent for {{company}}.\n'
                        'Customer issue: {{issue}}\n'
                        'Respond professionally and resolve in under 3 sentences.'
                    ),
                    'inputVariables': [
                        {'name': 'company'},
                        {'name': 'issue'}
                    ]
                }
            },
            'inferenceConfiguration': {
                'text': {'maxTokens': 256, 'temperature': 0.4}
            }
        }
    ],
    defaultVariant='default'
)

# Create version
version = bedrock_agent.create_prompt_version(
    promptIdentifier=prompt['id']
)

# Use prompt in converse
response = client.converse(
    modelId='anthropic.claude-3-5-haiku-20241022-v1:0',
    promptVariables={
        'company': {'text': 'Acme Corp'},
        'issue': {'text': 'My order has not arrived after 2 weeks'}
    },
    # reference via ARN
)
```

## Embeddings

```python
import json
import numpy as np

response = client.invoke_model(
    modelId='amazon.titan-embed-text-v2:0',
    body=json.dumps({
        'inputText': 'What is machine learning?',
        'dimensions': 1024,  # 256, 512, or 1024
        'normalize': True
    }),
    contentType='application/json'
)

embedding = json.loads(response['body'].read())['embedding']
# Returns list of 1024 floats
```

## Common Patterns

### Retry with Exponential Backoff

```python
import time
from botocore.exceptions import ClientError

def invoke_with_retry(client, model_id, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.converse(modelId=model_id, messages=messages)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### Cross-Region Inference Profile (for higher throughput)

```python
# Use inference profiles for auto-routing across regions
response = client.converse(
    modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',  # 'us.' prefix = cross-region
    messages=[...]
)
```

## Resources

- **Bedrock docs**: https://docs.aws.amazon.com/bedrock/
- **Converse API**: https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
- **Knowledge Bases**: https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html
- **Bedrock Flows**: https://docs.aws.amazon.com/bedrock/latest/userguide/flows.html
- **Guardrails**: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
- **Model IDs**: https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html
