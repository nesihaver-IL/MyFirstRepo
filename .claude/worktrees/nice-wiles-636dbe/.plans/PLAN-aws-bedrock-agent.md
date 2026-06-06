# Technical Plan: Building Your First AWS Bedrock Agent

## Overview
This document provides a comprehensive step-by-step plan to build and deploy your first AI agent using AWS Bedrock.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Phase 1: AWS Account & IAM Setup](#phase-1-aws-account--iam-setup)
3. [Phase 2: Enable Bedrock Model Access](#phase-2-enable-bedrock-model-access)
4. [Phase 3: Define Agent Use Case](#phase-3-define-agent-use-case)
5. [Phase 4: Create Knowledge Bases (Optional)](#phase-4-create-knowledge-bases-optional)
6. [Phase 5: Create Action Groups](#phase-5-create-action-groups)
7. [Phase 6: Build the Bedrock Agent](#phase-6-build-the-bedrock-agent)
8. [Phase 7: Test and Validate](#phase-7-test-and-validate)
9. [Phase 8: Deploy and Monitor](#phase-8-deploy-and-monitor)
10. [Best Practices](#best-practices)

---

## Prerequisites

### Required Knowledge
- [ ] Basic understanding of AWS services
- [ ] Familiarity with AWS Console or AWS CLI
- [ ] Understanding of REST APIs (if creating action groups)
- [ ] Basic knowledge of IAM roles and policies

### Required Resources
- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI installed (optional but recommended)
- [ ] Python 3.x or Node.js (for Lambda functions)
- [ ] Credit card for AWS billing (Bedrock is a paid service)

### Estimated Costs
- Model inference: Pay per token
- Knowledge base: S3 storage + vector database costs
- Lambda functions: Pay per invocation
- Estimated initial cost: $10-50 for testing phase

---

## Phase 1: AWS Account & IAM Setup

### Step 1.1: Verify AWS Account Access
```bash
# Verify AWS CLI is configured
aws sts get-caller-identity

# Check current region
aws configure get region
```

**Tasks:**
- [ ] Log into AWS Console
- [ ] Note your AWS Account ID
- [ ] Ensure you're in a supported region (us-east-1, us-west-2, etc.)
- [ ] Verify billing is set up

### Step 1.2: Create IAM Role for Bedrock Agent
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Tasks:**
- [ ] Navigate to IAM Console
- [ ] Create new role: "BedrockAgentRole"
- [ ] Attach trust policy (above)
- [ ] Attach policies:
  - [ ] AmazonBedrockFullAccess
  - [ ] CloudWatchLogsFullAccess (for logging)
  - [ ] Custom policy for Lambda invocation (if using action groups)

### Step 1.3: Create IAM Role for Lambda Functions (if needed)
**Tasks:**
- [ ] Create role: "BedrockAgentLambdaRole"
- [ ] Attach policies:
  - [ ] AWSLambdaBasicExecutionRole
  - [ ] Any custom policies for your Lambda's actions

---

## Phase 2: Enable Bedrock Model Access

### Step 2.1: Navigate to Bedrock Console
**Tasks:**
- [ ] Open AWS Console
- [ ] Search for "Amazon Bedrock"
- [ ] Select your preferred region

### Step 2.2: Request Model Access
**Tasks:**
- [ ] Click on "Model access" in left sidebar
- [ ] Click "Modify model access"
- [ ] Select models to enable:
  - [ ] **Anthropic Claude 3 Sonnet** (recommended for agents)
  - [ ] Anthropic Claude 3 Haiku (faster, cheaper)
  - [ ] Amazon Titan Text models (optional)
- [ ] Review end-user license agreements
- [ ] Submit access request
- [ ] Wait for approval (usually instant for most models)

### Step 2.3: Verify Model Access
```bash
# Using AWS CLI
aws bedrock list-foundation-models --region us-east-1
```

**Tasks:**
- [ ] Verify model status shows "Access granted"
- [ ] Test model invocation in Bedrock playground

---

## Phase 3: Define Agent Use Case

### Step 3.1: Document Your Agent's Purpose
**Questions to Answer:**
- What problem will this agent solve?
- Who are the end users?
- What actions should the agent perform?
- What information does the agent need access to?

### Step 3.2: Design Agent Capabilities

**Example Use Cases:**
1. **Customer Support Agent**
   - Actions: Query order status, process returns, update customer info
   - Knowledge: Product catalog, FAQ documents, return policies

2. **IT Help Desk Agent**
   - Actions: Reset passwords, create tickets, check system status
   - Knowledge: IT documentation, troubleshooting guides

3. **Data Analysis Agent**
   - Actions: Query databases, generate reports, visualize data
   - Knowledge: Data schemas, business metrics definitions

**Your Agent Design:**
```
Agent Name: [Your Agent Name]
Purpose: [Describe the purpose]

Capabilities:
1. [Capability 1]
2. [Capability 2]
3. [Capability 3]

Required Integrations:
- [ ] API endpoints
- [ ] Databases
- [ ] External services
```

### Step 3.3: Create Agent Instructions
Draft clear instructions for your agent:

```
You are a [role] assistant. Your purpose is to [goal].

When interacting with users:
- Always be [tone/style]
- Prioritize [values]
- If unsure, [fallback behavior]

You have access to:
- [Tool/knowledge 1]
- [Tool/knowledge 2]

Guidelines:
- [Guideline 1]
- [Guideline 2]
```

---

## Phase 4: Create Knowledge Bases (Optional)

### Step 4.1: Prepare Your Documents
**Tasks:**
- [ ] Gather source documents (PDF, TXT, HTML, Word)
- [ ] Organize documents by category
- [ ] Clean and format documents
- [ ] Remove sensitive information

### Step 4.2: Create S3 Bucket
```bash
# Create S3 bucket for knowledge base
aws s3 mb s3://my-bedrock-agent-kb --region us-east-1

# Upload documents
aws s3 cp ./documents/ s3://my-bedrock-agent-kb/ --recursive
```

**Tasks:**
- [ ] Create S3 bucket: `[your-agent-name]-kb-[random]`
- [ ] Enable versioning
- [ ] Upload documents to S3
- [ ] Set appropriate bucket policies

### Step 4.3: Create Knowledge Base in Bedrock
**Tasks:**
- [ ] Navigate to Bedrock Console → Knowledge bases
- [ ] Click "Create knowledge base"
- [ ] Configure:
  - Name: `[YourAgentName]KnowledgeBase`
  - Description: `[Describe the knowledge]`
  - IAM role: Create new or use existing
- [ ] Configure data source:
  - Source: S3
  - Bucket: Your S3 bucket
  - Chunking strategy: Default or custom
- [ ] Configure embeddings:
  - Model: Titan Embeddings G1 - Text
  - Vector database: Amazon OpenSearch Serverless (managed)
- [ ] Review and create
- [ ] Wait for sync to complete (5-30 minutes)

### Step 4.4: Test Knowledge Base
**Tasks:**
- [ ] Use "Test" feature in Bedrock console
- [ ] Ask sample questions
- [ ] Verify relevant documents are retrieved
- [ ] Adjust chunking if needed

---

## Phase 5: Create Action Groups

### Step 5.1: Define Required Actions
Document each action your agent needs:

```
Action 1: Get Order Status
- Input: order_id (string)
- Output: order details (object)
- Implementation: Lambda function calling order API

Action 2: Process Refund
- Input: order_id, reason (string)
- Output: refund confirmation (object)
- Implementation: Lambda function updating database
```

### Step 5.2: Create Lambda Functions
**Example Lambda (Python):**
```python
import json

def lambda_handler(event, context):
    # Parse the agent request
    action = event.get('actionGroup')
    api_path = event.get('apiPath')
    parameters = event.get('parameters', [])

    # Execute the action
    if api_path == '/getOrderStatus':
        order_id = next((p['value'] for p in parameters if p['name'] == 'order_id'), None)
        # Your business logic here
        result = get_order_status(order_id)

        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action,
                'apiPath': api_path,
                'httpMethod': 'GET',
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(result)
                    }
                }
            }
        }

def get_order_status(order_id):
    # Implement your logic
    return {'order_id': order_id, 'status': 'shipped'}
```

**Tasks:**
- [ ] Create Lambda function for each action
- [ ] Test Lambda functions independently
- [ ] Configure appropriate timeout (30-60 seconds)
- [ ] Set up error handling and logging
- [ ] Note Lambda ARN for agent configuration

### Step 5.3: Create OpenAPI Schema
Define your action group API:

```yaml
openapi: 3.0.0
info:
  title: My Agent Actions API
  version: 1.0.0
  description: Actions available to the Bedrock agent

paths:
  /getOrderStatus:
    get:
      summary: Get the status of an order
      description: Retrieves current status and details for a given order
      operationId: getOrderStatus
      parameters:
        - name: order_id
          in: query
          description: The unique identifier for the order
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Order status retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  order_id:
                    type: string
                  status:
                    type: string
                  tracking_number:
                    type: string

  /processRefund:
    post:
      summary: Process a refund for an order
      description: Initiates a refund for the specified order
      operationId: processRefund
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                order_id:
                  type: string
                reason:
                  type: string
      responses:
        '200':
          description: Refund processed successfully
```

**Tasks:**
- [ ] Create OpenAPI 3.0 schema
- [ ] Define all endpoints and parameters
- [ ] Add clear descriptions for each operation
- [ ] Save schema as JSON or YAML file

---

## Phase 6: Build the Bedrock Agent

### Step 6.1: Create the Agent
**Tasks:**
- [ ] Navigate to Bedrock Console → Agents
- [ ] Click "Create Agent"
- [ ] Configure basic details:
  - Agent name: `[YourAgentName]`
  - Description: `[Agent description]`
  - User input: Enable (default)
- [ ] Create new service role or use existing
- [ ] Click "Create"

### Step 6.2: Configure Agent Details
**Tasks:**
- [ ] Select foundation model:
  - **Recommended: Anthropic Claude 3 Sonnet**
  - Alternative: Claude 3 Haiku (faster/cheaper)
- [ ] Add agent instructions (from Phase 3.3)
- [ ] Configure additional settings:
  - [ ] Session timeout (default: 1 hour)
  - [ ] Enable CloudWatch logging
  - [ ] Tags (optional)

### Step 6.3: Add Action Groups
**Tasks:**
- [ ] Scroll to "Action groups" section
- [ ] Click "Add action group"
- [ ] Configure:
  - Name: `[ActionGroupName]`
  - Description: `[What these actions do]`
  - Action group type: Define with API schemas
  - Action group invocation: Lambda function
  - Lambda function: Select your Lambda ARN
  - API Schema: Upload or inline your OpenAPI schema
- [ ] Save action group
- [ ] Repeat for additional action groups if needed

### Step 6.4: Add Knowledge Base (if applicable)
**Tasks:**
- [ ] Scroll to "Knowledge bases" section
- [ ] Click "Add knowledge base"
- [ ] Select your knowledge base from Phase 4
- [ ] Add instructions for knowledge base usage:
  ```
  Use this knowledge base to answer questions about [topic].
  Always cite sources when using information from the knowledge base.
  ```
- [ ] Save

### Step 6.5: Configure Guardrails (Optional)
**Tasks:**
- [ ] Navigate to "Guardrails" section
- [ ] Click "Create guardrail" or use existing
- [ ] Configure filters:
  - [ ] Content filters (hate, violence, sexual, etc.)
  - [ ] Denied topics
  - [ ] Word filters
  - [ ] PII redaction
- [ ] Associate guardrail with agent

### Step 6.6: Prepare Agent
**Tasks:**
- [ ] Click "Prepare" button (top right)
- [ ] Wait for agent to prepare (1-2 minutes)
- [ ] Verify "Status: Prepared" shows

---

## Phase 7: Test and Validate

### Step 7.1: Test in Console
**Tasks:**
- [ ] Click "Test" button in agent console
- [ ] Run test conversations:
  - [ ] Test basic responses
  - [ ] Test knowledge base queries
  - [ ] Test action group invocations
  - [ ] Test error handling
  - [ ] Test multi-turn conversations

**Example Test Cases:**
```
Test 1: Basic Greeting
User: "Hello, who are you?"
Expected: Agent introduces itself based on instructions

Test 2: Knowledge Base Query
User: "What is [topic from your documents]?"
Expected: Accurate answer with source citations

Test 3: Action Invocation
User: "Can you check the status of order 12345?"
Expected: Agent calls Lambda and returns order status

Test 4: Multi-step Task
User: "I need to return order 12345 because it's damaged"
Expected: Agent checks order, confirms return eligibility, processes return
```

### Step 7.2: Review Trace Details
**Tasks:**
- [ ] Expand trace for each test
- [ ] Review:
  - [ ] Pre-processing steps
  - [ ] Orchestration flow
  - [ ] Knowledge base queries and results
  - [ ] Action group invocations
  - [ ] Post-processing
- [ ] Identify any issues or unexpected behavior

### Step 7.3: Iterate and Improve
**Tasks:**
- [ ] Refine agent instructions based on test results
- [ ] Adjust action group schemas if needed
- [ ] Update knowledge base documents
- [ ] Re-prepare agent after changes
- [ ] Re-test until satisfied

---

## Phase 8: Deploy and Monitor

### Step 8.1: Create Agent Alias
**Tasks:**
- [ ] Navigate to agent details
- [ ] Click "Create alias"
- [ ] Configure:
  - Alias name: `production` or `v1`
  - Description: Production version
  - Agent version: Select prepared version
- [ ] Create alias
- [ ] Note the Alias ID for application integration

### Step 8.2: Integrate with Your Application

**Python SDK Example:**
```python
import boto3
import json

# Initialize Bedrock Agent Runtime client
client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def invoke_agent(prompt, session_id):
    response = client.invoke_agent(
        agentId='YOUR_AGENT_ID',
        agentAliasId='YOUR_ALIAS_ID',
        sessionId=session_id,
        inputText=prompt
    )

    # Process the response stream
    event_stream = response['completion']
    full_response = ""

    for event in event_stream:
        if 'chunk' in event:
            chunk = event['chunk']
            if 'bytes' in chunk:
                full_response += chunk['bytes'].decode('utf-8')

    return full_response

# Example usage
result = invoke_agent("What is the status of order 12345?", "session-123")
print(result)
```

**Node.js SDK Example:**
```javascript
const { BedrockAgentRuntimeClient, InvokeAgentCommand } = require("@aws-sdk/client-bedrock-agent-runtime");

const client = new BedrockAgentRuntimeClient({ region: "us-east-1" });

async function invokeAgent(prompt, sessionId) {
  const command = new InvokeAgentCommand({
    agentId: "YOUR_AGENT_ID",
    agentAliasId: "YOUR_ALIAS_ID",
    sessionId: sessionId,
    inputText: prompt
  });

  const response = await client.send(command);

  // Process response stream
  let fullResponse = "";
  for await (const event of response.completion) {
    if (event.chunk && event.chunk.bytes) {
      fullResponse += new TextDecoder().decode(event.chunk.bytes);
    }
  }

  return fullResponse;
}

// Example usage
invokeAgent("What is the status of order 12345?", "session-123")
  .then(result => console.log(result));
```

**Tasks:**
- [ ] Install AWS SDK in your application
- [ ] Configure AWS credentials
- [ ] Implement agent invocation function
- [ ] Handle response streaming
- [ ] Implement session management
- [ ] Add error handling

### Step 8.3: Set Up Monitoring

**CloudWatch Metrics to Monitor:**
- Invocation count
- Invocation errors
- Latency
- Token usage
- Action group invocation success rate

**Tasks:**
- [ ] Create CloudWatch dashboard
- [ ] Set up alarms for:
  - [ ] High error rate (> 5%)
  - [ ] High latency (> 30 seconds)
  - [ ] Unusual invocation patterns
- [ ] Enable CloudWatch Logs Insights for debugging
- [ ] Set up cost alerts for Bedrock usage

### Step 8.4: Create CloudWatch Dashboard
```bash
# Example CloudWatch query for agent logs
aws logs insights query \
  --log-group-name /aws/bedrock/agents/YOUR_AGENT_ID \
  --start-time $(date -u -d '1 hour ago' +%s) \
  --end-time $(date -u +%s) \
  --query-string "fields @timestamp, @message | filter @message like /error/ | sort @timestamp desc"
```

**Tasks:**
- [ ] Create custom dashboard with key metrics
- [ ] Add widgets for invocation trends
- [ ] Monitor token consumption
- [ ] Track action group performance

---

## Best Practices

### Security
- [ ] Use least privilege IAM policies
- [ ] Enable CloudTrail for audit logging
- [ ] Implement guardrails to prevent misuse
- [ ] Encrypt sensitive data in transit and at rest
- [ ] Regularly rotate credentials
- [ ] Validate all action group inputs

### Performance
- [ ] Choose appropriate model (Haiku for speed, Sonnet for quality)
- [ ] Optimize Lambda functions for cold starts
- [ ] Keep knowledge base documents well-organized
- [ ] Use effective chunking strategies
- [ ] Monitor and optimize token usage
- [ ] Implement caching where appropriate

### Cost Optimization
- [ ] Start with smaller models (Haiku) for testing
- [ ] Monitor token consumption
- [ ] Set up billing alerts
- [ ] Use appropriate session timeouts
- [ ] Clean up unused resources
- [ ] Consider reserved capacity for production

### Reliability
- [ ] Implement comprehensive error handling
- [ ] Add fallback mechanisms
- [ ] Test edge cases thoroughly
- [ ] Version control your schemas and configurations
- [ ] Implement circuit breakers for external APIs
- [ ] Set up health checks

### Agent Design
- [ ] Write clear, specific instructions
- [ ] Provide examples in instructions
- [ ] Define clear boundaries for agent capabilities
- [ ] Implement graceful degradation
- [ ] Add conversation memory management
- [ ] Test with diverse user inputs

---

## Troubleshooting Common Issues

### Issue 1: Agent Not Invoking Actions
**Symptoms:** Agent responds but doesn't call Lambda functions

**Solutions:**
- [ ] Verify Lambda resource policy allows Bedrock invocation
- [ ] Check OpenAPI schema matches Lambda function signature
- [ ] Ensure action descriptions are clear
- [ ] Review agent instructions for action usage guidance

### Issue 2: Knowledge Base Not Returning Results
**Symptoms:** Agent says it doesn't have information that's in documents

**Solutions:**
- [ ] Verify knowledge base sync completed successfully
- [ ] Test knowledge base independently
- [ ] Adjust chunking strategy
- [ ] Improve document formatting
- [ ] Add more context to queries

### Issue 3: High Latency
**Symptoms:** Responses take too long

**Solutions:**
- [ ] Switch to faster model (Claude Haiku)
- [ ] Optimize Lambda functions
- [ ] Reduce knowledge base size or scope
- [ ] Simplify agent instructions
- [ ] Use streaming responses

### Issue 4: Unexpected Agent Behavior
**Symptoms:** Agent doesn't follow instructions

**Solutions:**
- [ ] Refine agent instructions with more specific guidance
- [ ] Add examples of desired behavior
- [ ] Use guardrails to constrain responses
- [ ] Review conversation traces
- [ ] Test with different prompts

---

## Next Steps After First Agent

### Enhance Your Agent
1. Add more action groups
2. Expand knowledge base
3. Implement advanced guardrails
4. Add custom preprocessing
5. Integrate with more systems

### Learn More
- [ ] AWS Bedrock documentation
- [ ] Claude prompt engineering guide
- [ ] OpenAPI specification
- [ ] Lambda best practices
- [ ] AWS Well-Architected Framework

### Build More Agents
- Customer service agent
- Data analysis agent
- Code review agent
- Content creation agent
- Research assistant agent

---

## Resources

### AWS Documentation
- [Amazon Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [OpenAPI Specification](https://swagger.io/specification/)

### AWS SDK References
- [Boto3 (Python) Bedrock Agent Runtime](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html)
- [AWS SDK for JavaScript](https://docs.aws.amazon.com/AWSJavaScriptSDK/v3/latest/clients/client-bedrock-agent-runtime/)

### Sample Code
- [AWS Bedrock Samples GitHub](https://github.com/aws-samples/amazon-bedrock-samples)
- [Bedrock Agent Examples](https://github.com/build-on-aws/amazon-bedrock-agents-quickstart)

---

## Checklist Summary

**Phase 1: Setup**
- [ ] AWS account configured
- [ ] IAM roles created
- [ ] AWS CLI installed and configured

**Phase 2: Model Access**
- [ ] Bedrock model access requested
- [ ] Model access approved
- [ ] Test invocation successful

**Phase 3: Planning**
- [ ] Use case defined
- [ ] Capabilities documented
- [ ] Agent instructions drafted

**Phase 4: Knowledge Base**
- [ ] Documents prepared
- [ ] S3 bucket created
- [ ] Knowledge base created and synced
- [ ] Knowledge base tested

**Phase 5: Actions**
- [ ] Actions defined
- [ ] Lambda functions created
- [ ] OpenAPI schema created
- [ ] Lambda functions tested

**Phase 6: Agent Creation**
- [ ] Agent created in Bedrock
- [ ] Model selected
- [ ] Action groups added
- [ ] Knowledge base attached
- [ ] Agent prepared

**Phase 7: Testing**
- [ ] Console testing completed
- [ ] All test cases passed
- [ ] Traces reviewed
- [ ] Iterations completed

**Phase 8: Deployment**
- [ ] Agent alias created
- [ ] Application integrated
- [ ] Monitoring configured
- [ ] Alerts set up

---

## Estimated Timeline

- **Phase 1-2 (Setup & Access):** 1-2 hours
- **Phase 3 (Planning):** 2-4 hours
- **Phase 4 (Knowledge Base):** 2-6 hours (depending on document volume)
- **Phase 5 (Actions):** 4-8 hours (depending on complexity)
- **Phase 6 (Agent Creation):** 1-2 hours
- **Phase 7 (Testing):** 4-8 hours
- **Phase 8 (Deployment):** 2-4 hours

**Total: 16-34 hours** for first agent (faster for subsequent agents)

---

## Success Criteria

Your Bedrock agent is ready for production when:
- [ ] Responds accurately to 95%+ of test queries
- [ ] Successfully invokes all action groups
- [ ] Returns relevant knowledge base information
- [ ] Maintains conversation context across turns
- [ ] Handles errors gracefully
- [ ] Meets latency requirements (< 30s for complex queries)
- [ ] Stays within budget constraints
- [ ] Monitoring and alerts are functional
- [ ] Documentation is complete

---

Good luck building your first AWS Bedrock Agent! 🚀
