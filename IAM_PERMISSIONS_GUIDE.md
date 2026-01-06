# IAM Permissions Guide for AWS Bedrock Agent Development

## Overview

This guide explains the IAM roles and policies required to build and operate AWS Bedrock Agents. There are two distinct types of permissions needed:

1. **Your IAM User Permissions** - What YOU need to create and manage the agent
2. **Agent Service Roles** - What the AGENT needs to run

---

## Part 1: Your IAM User Permissions

### Option A: Quick Start (Development/Testing)

For rapid development, attach these AWS managed policies to your IAM user:

```bash
# Get your IAM username
IAM_USER=$(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2)

# Attach managed policies
aws iam attach-user-policy --user-name $IAM_USER --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
aws iam attach-user-policy --user-name $IAM_USER --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
aws iam attach-user-policy --user-name $IAM_USER --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess
aws iam attach-user-policy --user-name $IAM_USER --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-user-policy --user-name $IAM_USER --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

**Pros:** Simple, fast to set up
**Cons:** Broad permissions, not suitable for production

### Option B: Production Setup (Least Privilege)

Use the custom policy created by the `setup-iam-permissions.sh` script:

```bash
# Run the setup script
chmod +x setup-iam-permissions.sh
./setup-iam-permissions.sh

# Attach the custom policy to your user
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IAM_USER=$(aws sts get-caller-identity --query Arn --output text | cut -d'/' -f2)

aws iam attach-user-policy \
  --user-name $IAM_USER \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/BedrockAgentDeveloperPolicy
```

**Pros:** Follows least privilege principle, production-ready
**Cons:** More restrictive, may need adjustments for specific use cases

---

## Part 2: Service Roles for Your Bedrock Agent

### Role 1: Bedrock Agent Execution Role

**Purpose:** This role is assumed by the Bedrock Agent service to invoke models, Lambda functions, and access knowledge bases.

**When to use:** Specify this role when creating your Bedrock Agent in the console or via API.

**Key Permissions:**
- Invoke Claude models (Sonnet, Haiku)
- Call Lambda functions for action groups
- Access knowledge bases
- Read S3 objects for knowledge base documents
- Write CloudWatch logs

**Created by:** The `setup-iam-permissions.sh` script creates this as `BedrockAgentExecutionRole`

### Role 2: Lambda Execution Role

**Purpose:** This role is assumed by Lambda functions that implement your agent's action groups.

**When to use:** Specify this role when creating Lambda functions for your agent's actions.

**Key Permissions:**
- CloudWatch Logs (basic execution)
- Custom permissions for your business logic (DynamoDB, APIs, etc.)

**Created by:** The `setup-iam-permissions.sh` script creates this as `BedrockAgentLambdaRole`

**Note:** You'll need to add custom permissions based on what your Lambda functions do.

### Role 3: Knowledge Base Role

**Purpose:** This role is assumed by Bedrock Knowledge Base service to access your documents and create embeddings.

**When to use:** Specify this role when creating a Knowledge Base.

**Key Permissions:**
- Read S3 objects (your documents)
- Invoke Titan Embeddings model
- Access OpenSearch Serverless collection

**Created by:** The `setup-iam-permissions.sh` script creates this as `BedrockKnowledgeBaseRole`

---

## Permission Requirements by Task

### Creating a Bedrock Agent
**Your user needs:**
- `bedrock:CreateAgent`
- `bedrock:UpdateAgent`
- `iam:PassRole` (to assign the execution role to the agent)

**The agent needs:**
- Execution role with `bedrock:InvokeModel` permission

### Adding Action Groups
**Your user needs:**
- `bedrock:CreateActionGroup`
- `lambda:GetFunction` (to verify Lambda exists)
- `lambda:AddPermission` (to allow agent to invoke Lambda)

**The agent needs:**
- Execution role with `lambda:InvokeFunction` permission

### Creating Knowledge Base
**Your user needs:**
- `bedrock:CreateKnowledgeBase`
- `s3:CreateBucket`
- `s3:PutObject`
- `aoss:CreateCollection`

**The knowledge base needs:**
- Knowledge Base role with S3 read and embeddings permissions

### Testing and Invocation
**Your user needs:**
- `bedrock-agent-runtime:InvokeAgent`
- `bedrock:GetAgent`

---

## Security Best Practices

### 1. Least Privilege Principle
- Start with minimal permissions
- Add permissions as needed
- Review permissions regularly

### 2. Resource-Based Restrictions
```json
{
  "Sid": "RestrictToBedrockResources",
  "Effect": "Allow",
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:*:ACCOUNT_ID:function:bedrock-*"
}
```

### 3. Condition Keys for Added Security
```json
{
  "Condition": {
    "StringEquals": {
      "aws:SourceAccount": "YOUR_ACCOUNT_ID"
    },
    "ArnLike": {
      "aws:SourceArn": "arn:aws:bedrock:REGION:ACCOUNT_ID:agent/*"
    }
  }
}
```

### 4. Separate Environments
- Use different IAM roles for dev, staging, production
- Use resource tags to enforce environment boundaries

### 5. Enable CloudTrail
```bash
# Monitor all Bedrock API calls
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateAgent
```

---

## Common Permission Issues and Solutions

### Issue 1: "Access Denied" when creating agent

**Solution:** Verify your user has these permissions:
```bash
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --query Arn --output text) \
  --action-names bedrock:CreateAgent bedrock:UpdateAgent \
  --resource-arns "arn:aws:bedrock:*:*:agent/*"
```

### Issue 2: Agent can't invoke Lambda functions

**Cause:** Lambda resource policy doesn't allow Bedrock service

**Solution:** Add Lambda permission:
```bash
aws lambda add-permission \
  --function-name your-function-name \
  --statement-id bedrock-agent-access \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-arn "arn:aws:bedrock:REGION:ACCOUNT_ID:agent/AGENT_ID"
```

### Issue 3: Knowledge Base can't access S3

**Solution:** Verify S3 bucket policy allows the Knowledge Base role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/BedrockKnowledgeBaseRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-kb-bucket",
        "arn:aws:s3:::your-kb-bucket/*"
      ]
    }
  ]
}
```

### Issue 4: "Invalid model ID" error

**Cause:** Model access not enabled in Bedrock

**Solution:**
1. Go to AWS Console → Bedrock → Model access
2. Request access to required models
3. Wait for approval (usually instant)

---

## Verification Checklist

Before creating your Bedrock Agent, verify:

- [ ] Your IAM user has `BedrockAgentDeveloperPolicy` or equivalent attached
- [ ] You've created `BedrockAgentExecutionRole`
- [ ] You've created `BedrockAgentLambdaRole` (if using action groups)
- [ ] You've created `BedrockKnowledgeBaseRole` (if using knowledge bases)
- [ ] Model access is enabled for Claude 3 Sonnet/Haiku
- [ ] Your Lambda functions have proper resource policies
- [ ] Your S3 bucket allows the Knowledge Base role (if applicable)
- [ ] CloudWatch log groups are created or roles have permission to create them

---

## Quick Reference: Role ARNs

After running `setup-iam-permissions.sh`, use these ARNs:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}

# Bedrock Agent Execution Role
AGENT_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/BedrockAgentExecutionRole"

# Lambda Execution Role
LAMBDA_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/BedrockAgentLambdaRole"

# Knowledge Base Role
KB_ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/BedrockKnowledgeBaseRole"
```

Use these when creating resources:
- **Creating Agent:** Use `AGENT_ROLE_ARN`
- **Creating Lambda:** Use `LAMBDA_ROLE_ARN`
- **Creating Knowledge Base:** Use `KB_ROLE_ARN`

---

## Additional Resources

- [AWS Bedrock IAM Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Lambda Resource Policies](https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html)
- [Bedrock Agent Permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-permissions.html)

---

## Summary

**For your IAM user (developer):**
- Use `BedrockAgentDeveloperPolicy` (created by setup script)
- OR attach AWS managed policies for quick start

**For the Bedrock Agent itself:**
- Use `BedrockAgentExecutionRole` (created by setup script)

**For Lambda functions:**
- Use `BedrockAgentLambdaRole` (created by setup script)
- Add custom permissions for your business logic

**For Knowledge Bases:**
- Use `BedrockKnowledgeBaseRole` (created by setup script)

Run `./setup-iam-permissions.sh` to create all necessary roles automatically!
