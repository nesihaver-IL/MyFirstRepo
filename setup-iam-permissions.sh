#!/bin/bash

# AWS Bedrock Agent IAM Setup Script
# This script creates the necessary IAM roles and policies for your Bedrock Agent

set -e

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-east-1}

echo "Setting up IAM roles for AWS Bedrock Agent..."
echo "Account ID: $ACCOUNT_ID"
echo "Region: $REGION"

# 1. Create Bedrock Agent Execution Role
echo "Creating Bedrock Agent Execution Role..."

cat > /tmp/bedrock-agent-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "$ACCOUNT_ID"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:bedrock:$REGION:$ACCOUNT_ID:agent/*"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name BedrockAgentExecutionRole \
  --assume-role-policy-document file:///tmp/bedrock-agent-trust-policy.json \
  --description "Execution role for AWS Bedrock Agent" || echo "Role already exists"

# 2. Create and attach Bedrock Agent permissions policy
cat > /tmp/bedrock-agent-permissions.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeBedrockModels",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-*",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-*",
        "arn:aws:bedrock:*::foundation-model/amazon.titan-*"
      ]
    },
    {
      "Sid": "InvokeLambdaActions",
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:$REGION:$ACCOUNT_ID:function:*bedrock*"
    },
    {
      "Sid": "AccessKnowledgeBase",
      "Effect": "Allow",
      "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
      ],
      "Resource": "arn:aws:bedrock:$REGION:$ACCOUNT_ID:knowledge-base/*"
    },
    {
      "Sid": "S3KnowledgeBaseAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::*bedrock*kb*",
        "arn:aws:s3:::*bedrock*kb*/*"
      ]
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:$REGION:$ACCOUNT_ID:log-group:/aws/bedrock/*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name BedrockAgentExecutionRole \
  --policy-name BedrockAgentPermissions \
  --policy-document file:///tmp/bedrock-agent-permissions.json

echo "✓ Bedrock Agent Execution Role created"

# 3. Create Lambda Execution Role for Action Groups
echo "Creating Lambda Execution Role for Action Groups..."

cat > /tmp/lambda-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name BedrockAgentLambdaRole \
  --assume-role-policy-document file:///tmp/lambda-trust-policy.json \
  --description "Execution role for Bedrock Agent Lambda functions" || echo "Role already exists"

# Attach AWS managed policy for Lambda basic execution
aws iam attach-role-policy \
  --role-name BedrockAgentLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo "✓ Lambda Execution Role created"

# 4. Create Knowledge Base Role
echo "Creating Knowledge Base Role..."

cat > /tmp/kb-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "$ACCOUNT_ID"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name BedrockKnowledgeBaseRole \
  --assume-role-policy-document file:///tmp/kb-trust-policy.json \
  --description "Role for Bedrock Knowledge Base" || echo "Role already exists"

cat > /tmp/kb-permissions.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::*bedrock*kb*",
        "arn:aws:s3:::*bedrock*kb*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "aoss:APIAccessAll"
      ],
      "Resource": "arn:aws:aoss:$REGION:$ACCOUNT_ID:collection/*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name BedrockKnowledgeBaseRole \
  --policy-name KnowledgeBasePermissions \
  --policy-document file:///tmp/kb-permissions.json

echo "✓ Knowledge Base Role created"

# 5. Create Developer/User Policy (to attach to your IAM user)
echo "Creating Developer Policy for IAM User..."

cat > /tmp/developer-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAgentManagement",
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "bedrock-agent:*",
        "bedrock-agent-runtime:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "IAMRoleManagement",
      "Effect": "Allow",
      "Action": [
        "iam:GetRole",
        "iam:GetRolePolicy",
        "iam:ListRolePolicies",
        "iam:ListAttachedRolePolicies",
        "iam:PassRole"
      ],
      "Resource": [
        "arn:aws:iam::$ACCOUNT_ID:role/BedrockAgent*",
        "arn:aws:iam::$ACCOUNT_ID:role/AmazonBedrockExecutionRoleForAgents*"
      ]
    },
    {
      "Sid": "LambdaManagement",
      "Effect": "Allow",
      "Action": [
        "lambda:CreateFunction",
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:DeleteFunction",
        "lambda:GetFunction",
        "lambda:InvokeFunction",
        "lambda:ListFunctions",
        "lambda:AddPermission",
        "lambda:RemovePermission",
        "lambda:GetPolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "S3KnowledgeBase",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetBucketLocation",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "*"
    },
    {
      "Sid": "OpenSearchServerless",
      "Effect": "Allow",
      "Action": [
        "aoss:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchMonitoring",
      "Effect": "Allow",
      "Action": [
        "logs:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name BedrockAgentDeveloperPolicy \
  --policy-document file:///tmp/developer-policy.json \
  --description "Policy for developers building Bedrock Agents" 2>/dev/null || echo "Policy already exists"

echo ""
echo "========================================="
echo "IAM Setup Complete!"
echo "========================================="
echo ""
echo "Created Roles:"
echo "  1. BedrockAgentExecutionRole - For the Bedrock Agent"
echo "  2. BedrockAgentLambdaRole - For Lambda functions"
echo "  3. BedrockKnowledgeBaseRole - For Knowledge Bases"
echo ""
echo "Created Policy:"
echo "  - BedrockAgentDeveloperPolicy (arn:aws:iam::$ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy)"
echo ""
echo "Next Steps:"
echo "  1. Attach BedrockAgentDeveloperPolicy to your IAM user:"
echo "     aws iam attach-user-policy --user-name YOUR_USERNAME --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/BedrockAgentDeveloperPolicy"
echo ""
echo "  2. Use BedrockAgentExecutionRole when creating your Bedrock Agent"
echo "  3. Use BedrockAgentLambdaRole when creating Lambda functions"
echo "  4. Use BedrockKnowledgeBaseRole when creating Knowledge Bases"
echo ""

# Clean up temp files
rm /tmp/bedrock-agent-trust-policy.json
rm /tmp/bedrock-agent-permissions.json
rm /tmp/lambda-trust-policy.json
rm /tmp/kb-trust-policy.json
rm /tmp/kb-permissions.json
rm /tmp/developer-policy.json
