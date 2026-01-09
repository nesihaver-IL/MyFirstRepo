# Setup Guide - AWS AI Agent

## Prerequisites

- AWS Account with Bedrock access
- Python 3.11+
- AWS CLI v2
- Terraform (for infrastructure)

## Step 1: AWS Configuration

### Enable Bedrock Models

1. Go to AWS Console → Bedrock → Model access
2. Request access to Claude models
3. Wait for approval (usually instant)

### Create IAM User/Role

```bash
# Create IAM user for development
aws iam create-user --user-name bedrock-dev

# Attach Bedrock policy
aws iam attach-user-policy \
  --user-name bedrock-dev \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

### Configure AWS CLI

```bash
aws configure
# Enter Access Key, Secret Key, Region (us-east-1 recommended)
```

## Step 2: Project Setup

### Clone and Install

```bash
# Navigate to project
cd 01-personal/aws-ai-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create `.env` file:

```env
AWS_REGION=us-east-1
AWS_PROFILE=default
LOG_LEVEL=INFO
```

## Step 3: Verify Setup

```bash
# Test AWS connection
aws bedrock list-foundation-models --region us-east-1

# Run test script
python -m src.utils.test_connection
```

## Step 4: Infrastructure (Optional)

```bash
# Deploy with Terraform
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

## Troubleshooting

### "Access Denied" errors
- Verify IAM permissions
- Check model access is enabled in Bedrock console

### "Region not supported"
- Bedrock is available in specific regions
- Use us-east-1 or us-west-2

### Connection timeouts
- Check VPC/network configuration
- Verify security group rules
