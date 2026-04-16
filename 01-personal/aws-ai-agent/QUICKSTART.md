# AWS AI Agent — Quickstart Guide

Get the agent running locally in ~15 minutes.

---

## Prerequisites

- Python 3.11+
- AWS account (free tier eligible)
- AWS CLI configured
- Anthropic API key

---

## Setup (15 min)

### 1. Clone and Setup

```bash
cd 01-personal/aws-ai-agent

# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS

```bash
# Configure AWS credentials
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Region (us-east-1)

# Verify configuration
aws sts get-caller-identity
# Expected output: Shows your AWS account info
```

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
nano .env
# or
code .env
```

**Required settings:**
```
ANTHROPIC_API_KEY=sk-ant-...
AWS_REGION=us-east-1
AGENT_NAME=my-agent
```

### 4. Run Locally

```bash
# Test agent is working
python -m src.agent.main

# Expected: Agent initialized and ready for input
```

✅ **Agent is running locally!**

---

## Try It Out

### Simple Test

```python
# In interactive shell
python -c "
from src.agent import Agent

agent = Agent()
response = agent.run('What are my available tools?')
print(response)
"
```

### Interactive Chat

```bash
python src/agent/interactive.py
# Type your messages and see agent responses
```

### With Tools

```python
from src.agent import Agent
from src.tools import ListTables, QueryDatabase

agent = Agent(tools=[
    ListTables(),
    QueryDatabase()
])

response = agent.run('What tables are in my DynamoDB?')
print(response)
```

---

## Deploy to AWS Lambda

Optional: Run agent as serverless function.

### 1. Build Package

```bash
bash scripts/build_lambda.sh
# Creates deployment.zip
```

### 2. Deploy

```bash
bash scripts/deploy_lambda.sh
# Uploads to AWS Lambda

# View outputs
aws lambda get-function --function-name aws-ai-agent
```

### 3. Invoke

```bash
# Invoke Lambda function
aws lambda invoke \
  --function-name aws-ai-agent \
  --payload '{"input":"What time is it?"}' \
  response.json

# View response
cat response.json
```

---

## Project Structure

```
aws-ai-agent/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point
│   │   ├── reasoning.py         # Agent loop logic
│   │   └── memory.py            # Conversation memory
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── aws_tools.py         # AWS Lambda, DynamoDB, etc.
│   │   ├── web_tools.py         # HTTP requests, APIs
│   │   └── utils.py             # Helper functions
│   └── models/
│       └── schemas.py           # Data models
├── tests/
│   ├── test_agent.py
│   ├── test_tools.py
│   └── test_integrations.py
├── infrastructure/
│   └── terraform/               # IaC configs
├── scripts/
│   ├── build_lambda.sh
│   ├── deploy_lambda.sh
│   └── test.sh
└── QUICKSTART.md                # This file
```

---

## Common Commands

```bash
# Run agent locally
python -m src.agent.main

# Interactive mode
python src/agent/interactive.py

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_agent.py::test_agent_initialization -v

# Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# View Lambda logs
aws logs tail /aws/lambda/aws-ai-agent --follow

# Invoke Lambda
aws lambda invoke --function-name aws-ai-agent --payload '{}' response.json
```

---

## Add a Custom Tool

### 1. Define Tool

```python
# src/tools/custom_tools.py
from src.agent.tools import BaseTool

class MyCustomTool(BaseTool):
    """Description of what this tool does."""
    
    def __init__(self):
        self.name = "my_tool"
        self.description = "Does something useful"
    
    def run(self, input_str: str) -> str:
        """Execute the tool."""
        result = do_something(input_str)
        return result
```

### 2. Register Tool

```python
# src/agent/main.py
from src.tools.custom_tools import MyCustomTool

agent = Agent(tools=[
    MyCustomTool(),
    # Other tools...
])
```

### 3. Use in Agent

```
Agent: I can use these tools: [my_tool, ...]
You: Use my_tool to get data
Agent: <my_tool>input</my_tool>
[Tool executes...]
Agent: The result is...
```

---

## Troubleshooting

### "ModuleNotFoundError: anthropic"
```bash
# Activate venv and reinstall
source .venv/bin/activate
pip install -r requirements.txt
```

### "NoCredentialsError" from AWS
```bash
# Configure AWS
aws configure

# Verify credentials
aws sts get-caller-identity
```

### Agent times out or runs too long
```python
# Add timeout to agent loop
agent = Agent(
    max_iterations=5,           # Stop after 5 iterations
    iteration_timeout_seconds=30 # 30 second timeout per iteration
)
```

### Lambda deployment fails
```bash
# Check IAM permissions
aws iam get-user

# Verify Lambda role has required permissions
aws iam get-role-policy --role-name aws-ai-agent-lambda-role \
  --policy-name aws-ai-agent-policy
```

### Agent doesn't have access to tools
```bash
# Verify tools are imported and registered
python -c "
from src.agent import Agent
agent = Agent()
print('Available tools:', [t.name for t in agent.tools])
"
```

---

## Architecture Decision

This project is a **generic framework**, not domain-specific.

- ✅ Reusable agent loop and tool patterns
- ✅ No Garmin-specific code (see `garmin-health/` for that)
- ✅ Template for other agent projects

See [DECISIONS.md](DECISIONS.md) for architecture choices.

---

## Next Steps

- **Full documentation**: [README.md](README.md)
- **Development setup**: [CLAUDE.md](CLAUDE.md)
- **Architecture**: [DECISIONS.md](DECISIONS.md)
- **Active work**: [TODO.md](TODO.md)

---

**Last updated**: 2026-04-13  
**Tested on**: Python 3.11+, macOS 14, Ubuntu 22.04
