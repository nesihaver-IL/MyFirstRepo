# AWS Bedrock Cheatsheet

## Quick Reference

### Available Models

| Model | ID | Use Case |
|-------|-----|----------|
| Claude 3.5 Sonnet | anthropic.claude-3-5-sonnet-20241022-v2:0 | General purpose |
| Claude 3 Haiku | anthropic.claude-3-haiku-20240307-v1:0 | Fast, cost-effective |
| Llama 3.1 70B | meta.llama3-1-70b-instruct-v1:0 | Open source option |
| Titan Text | amazon.titan-text-express-v1 | AWS native |

### Boto3 Setup

```python
import boto3

# Create Bedrock runtime client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'
)
```

### Invoke Model (Claude)

```python
import json

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    })
)

result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

### Converse API (Recommended)

```python
response = bedrock.converse(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[
        {"role": "user", "content": [{"text": "Hello!"}]}
    ],
    inferenceConfig={
        "maxTokens": 1024,
        "temperature": 0.7
    }
)

print(response['output']['message']['content'][0]['text'])
```

### Streaming

```python
response = bedrock.converse_stream(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[{"role": "user", "content": [{"text": "Hello!"}]}]
)

for event in response['stream']:
    if 'contentBlockDelta' in event:
        print(event['contentBlockDelta']['delta']['text'], end='')
```

### Tool Calling

```python
tools = [{
    "toolSpec": {
        "name": "get_weather",
        "description": "Get current weather",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
}]

response = bedrock.converse(
    modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
    messages=[{"role": "user", "content": [{"text": "What's the weather in Seattle?"}]}],
    toolConfig={"tools": tools}
)
```

### Knowledge Bases

```python
bedrock_agent = boto3.client('bedrock-agent-runtime')

response = bedrock_agent.retrieve_and_generate(
    input={'text': 'What is the return policy?'},
    retrieveAndGenerateConfiguration={
        'type': 'KNOWLEDGE_BASE',
        'knowledgeBaseConfiguration': {
            'knowledgeBaseId': 'KB_ID',
            'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
        }
    }
)
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| AccessDeniedException | Model not enabled | Enable in Bedrock console |
| ValidationException | Invalid model ID | Check model ID spelling |
| ThrottlingException | Rate limit | Implement exponential backoff |

## Useful Links

- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/APIReference/)
- [Model IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
