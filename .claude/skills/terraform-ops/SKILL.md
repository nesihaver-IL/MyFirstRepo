---
name: terraform-ops
description: Manage Terraform infrastructure for AWS projects. Use when planning, applying, or troubleshooting Terraform modules for Lambda, DynamoDB, API Gateway, EventBridge, or IAM. Triggers on keywords like terraform plan, deploy infra, tfstate, infrastructure, deploy aws.
---

# Terraform Ops

Manage AWS infrastructure using Terraform across `garmin-health/backend/terraform/` and `aws-ai-agent/` projects.

## Purpose

Handle all Terraform lifecycle operations:
- Read and validate module structure
- Plan infrastructure changes safely
- Apply deployments with pre-flight checks
- Inspect `tfstate` for resource status
- Troubleshoot IAM, Lambda, DynamoDB, API GW, EventBridge issues

## When to Use

- Before any infra change (`terraform plan` first)
- When deploying or destroying AWS resources
- When Lambda or API GW routes stop working
- When adding new DynamoDB tables or IAM roles
- When reviewing existing infrastructure state
- Before running `scripts/deploy.sh` or `scripts/destroy.sh`

## Project Locations

| Project | Terraform Path | Deploy Script |
|---------|---------------|---------------|
| Garmin Health | `01-personal/garmin-health/backend/terraform/` | `backend/scripts/deploy.sh` |
| AWS AI Agent | `01-personal/aws-ai-agent/` | check project CLAUDE.md |

## AWS Stack (Garmin Health)

| Resource | Purpose |
|----------|---------|
| AWS Lambda (×4) | fetch, oauth, webhook, analyzer functions |
| API Gateway | REST API layer |
| DynamoDB | Activity + wellness data storage |
| EventBridge | Scheduled triggers |
| IAM | Lambda execution roles + policies |

## How It Works

1. **Read module structure**: Understand variables, outputs, and resources
2. **Pre-flight check**: Verify `.env` / `terraform.tfvars` are populated
3. **Plan**: Run `terraform plan` to preview changes
4. **Review**: Confirm no destructive changes before applying
5. **Apply**: Execute with `terraform apply`
6. **Verify**: Check outputs and resource state

## Usage

```
/terraform-ops
```

Or natural language:
```
"plan the garmin infra changes"
"check what terraform will destroy before I run deploy.sh"
"show me the current tfstate for DynamoDB"
"I need to add a new Lambda — help me update the terraform module"
```

## Pre-flight Checklist

Before any `terraform apply`:

```bash
# Confirm config files are filled (never commit actual values)
ls 01-personal/garmin-health/backend/config/
# Should see: .env (not .env.example), terraform.tfvars (not .tfvars.example)

# Navigate to terraform dir
cd 01-personal/garmin-health/backend/terraform

# Init (first time or after module changes)
terraform init

# Plan — always do this first
terraform plan -var-file="../config/terraform.tfvars"

# Apply only after reviewing plan output
terraform apply -var-file="../config/terraform.tfvars"
```

## Common Operations

### Check current state
```bash
terraform show
terraform state list
terraform state show aws_dynamodb_table.garmin_activities
```

### Lambda deployment
```bash
# Build Lambda zip (run from backend/)
bash scripts/deploy.sh

# Or manually
cd lambda/fetch-activities
zip -r function.zip .
aws lambda update-function-code --function-name garmin-fetch --zip-file fileb://function.zip
```

### Destroy (destructive — confirm first)
```bash
terraform plan -destroy  # Preview destruction
terraform destroy -var-file="../config/terraform.tfvars"  # Only after confirmation
```

### Targeted operations
```bash
# Apply only one resource
terraform apply -target=aws_lambda_function.analyzer

# Destroy only one resource
terraform destroy -target=aws_api_gateway_rest_api.garmin_api
```

## Secrets Management

**Critical**: Never commit real values.
- Use `.env.example` and `terraform.tfvars.example` as templates
- Real values go in `.env` and `terraform.tfvars` (gitignored)
- Lambda env vars come from `config/.env`
- Infrastructure vars come from `config/terraform.tfvars`

## Troubleshooting

### Lambda not deploying
```bash
# Check function exists
aws lambda get-function --function-name garmin-fetch

# Check logs
aws logs tail /aws/lambda/garmin-fetch --follow
```

### DynamoDB access denied
```bash
# Review IAM policy attached to Lambda role
terraform state show aws_iam_role_policy.lambda_dynamodb
```

### API Gateway 502
```bash
# Check Lambda integration
terraform state show aws_api_gateway_integration.fetch_integration
```

## Integration with Workflow

```
/exploration-phase (understand infra)
    ↓
/terraform-ops (plan changes)
    ↓
[Review plan output with user]
    ↓
/terraform-ops (apply)
    ↓
/update-docs
```

## Security Rules

- Never `terraform apply` without reviewing `terraform plan` first
- Never commit `.env` or `terraform.tfvars` with real values
- Always use IAM least-privilege for Lambda roles
- Review EventBridge rules before enabling scheduled triggers
- Tag all resources with `project = "garmin-health"` or `project = "aws-ai-agent"`
