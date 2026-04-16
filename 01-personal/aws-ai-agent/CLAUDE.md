# CLAUDE.md - AWS AI Agent Project

## Project Overview

Generic AWS Bedrock AI agent framework for learning and experimentation. Focus is on **reusable patterns** (not domain-specific logic) for agent architectures, tool integration, and cloud deployment. Used as a template for other agent projects (e.g., Garmin health agent, product knowledge agent).

## Technology Stack

| Component | Tech | Notes |
|-----------|------|-------|
| Language | Python 3.11+ | — |
| AI Models | AWS Bedrock | Claude, Anthropic models |
| Agent Framework | Boto3 (low-level) or Strands SDK | `aws-strands` skill for high-level patterns |
| Infrastructure | Terraform | AWS Lambda, DynamoDB, API Gateway |
| Vector Store | Amazon OpenSearch / Pinecone | For RAG |
| Memory | In-process or DynamoDB | Conversation history |

## Project Structure

```
aws-ai-agent/
├── src/
│   ├── agent/          # Core agent reasoning loop
│   ├── tools/          # Callable tool/action functions
│   ├── memory/         # Conversation & state management
│   ├── models/         # Data models & schemas
│   └── utils/          # Shared utilities
├── infrastructure/     # Terraform configs (Lambda, API GW, IAM)
├── tests/              # Unit + integration tests
├── docs/               # Garmin JSON data (historical, pending migration)
└── experiments/        # POC explorations (not for production)
```

## Development Setup

```bash
# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Run locally
python -m src.agent.main

# Run tests
python -m pytest tests/ -v

# Deploy infrastructure
cd infrastructure
terraform init
terraform plan
terraform apply
```

## Claude Code Skills for This Project

| Skill | When to Use |
|-------|-----------|
| `aws-strands` | Building agent with Strands SDK (ReAct patterns, tool orchestration) |
| `aws-bedrock` | Invoking models directly, RAG, Guardrails, Prompt Management |
| `aws-lambda` | Deploying tools as Lambda functions (agent backends) |
| `terraform-ops` | Planning/applying infrastructure changes |
| `test-runner` | Running pytest suite before commit |

## Key Architecture Concepts

- **Agent Loop**: Perception → Reasoning → Action → Observation → repeat
- **Tools**: Callable functions agent can invoke (AWS Lambda, APIs, databases)
- **Tool Definitions**: JSON schema describing parameters and expected outputs
- **Prompts**: System instructions guiding agent reasoning
- **Memory**: Maintains conversation history and state between interactions
- **Guardrails**: Input validation, output filtering, safety constraints

## Important Notes

- **This is a framework**: No domain-specific logic — keep patterns generic
- **AWS permissions**: Always start with minimal permissions, use IAM roles
- **Cost tracking**: Monitor AWS Cost Explorer regularly (Bedrock + Lambda calls are charged)
- **Experiments first**: Use `experiments/` for POCs before moving to `src/`
- **API documentation**: Document all tool signatures in code comments

## Data Files

Garmin JSON exports currently stored here (historical location):
- `docs/nesihaver@gmail.com_0_summarizedActivities.json`
- `docs/sleep_all_merged.json`
- `docs/wellness_all_merged.json`

**TODO**: Migrate to `01-personal/garmin-health/data/raw/` using `data-pipeline` skill.

## Testing & Quality

- Write tests for all agent tools
- Mock AWS Bedrock calls in unit tests
- Use integration tests for end-to-end flows
- Run full test suite before every commit (`test-runner` skill)
- Run `security-audit` skill before committing

## Deployment

```bash
# Plan infrastructure changes
terraform plan -var-file="environment.tfvars"

# Apply changes
terraform apply -var-file="environment.tfvars"

# Verify deployment
aws lambda list-functions
aws apigateway get-rest-apis
```

## Resources

- [AWS Bedrock Agent Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Agent SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent.html)
- [Strands Agents SDK](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-agents-arn.html)
- [Lambda Function Development](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
