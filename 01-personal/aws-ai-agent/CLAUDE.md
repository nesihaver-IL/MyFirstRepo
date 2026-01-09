# CLAUDE.md - AWS AI Agent Project

## Project Overview

A learning project to build an AI agent using AWS Bedrock, focusing on understanding agent architectures, tool integration, and cloud deployment patterns.

## Technology Stack

- **Language**: Python 3.11+
- **AI Platform**: AWS Bedrock
- **Framework**: Boto3, LangChain (optional)
- **Infrastructure**: Terraform/CloudFormation
- **Vector Store**: Amazon OpenSearch / Pinecone

## Project Structure

```
aws-ai-agent/
├── src/
│   ├── agent/          # Core agent logic
│   ├── tools/          # Agent tools/capabilities
│   ├── memory/         # Conversation memory
│   └── utils/          # Utility functions
├── experiments/        # POC experiments
├── infrastructure/     # IaC templates
└── environments/       # Environment configs
```

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS
aws configure

# Run locally
python -m src.agent.main
```

## Key Concepts

- **Agent Loop**: Reasoning → Action → Observation cycle
- **Tools**: Functions the agent can invoke
- **Memory**: Conversation history and context management
- **Guardrails**: Input/output filtering for safety

## Important Notes

- Always test with minimal permissions first
- Use dev environment for experiments
- Document all API interactions
- Track costs in AWS Cost Explorer

## Resources

- [AWS Bedrock Agent Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Bedrock Agent SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent.html)
