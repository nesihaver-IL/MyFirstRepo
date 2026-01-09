# AWS AI Agent

An AI agent built on AWS Bedrock for learning cloud-native agent development.

## Features

- [ ] Basic agent with Bedrock Claude model
- [ ] Custom tool integration
- [ ] Conversation memory
- [ ] RAG with knowledge bases
- [ ] Multi-agent orchestration

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Run the agent
python -m src.agent.main
```

## Architecture

See [docs/architecture.md](./docs/architecture.md) for detailed architecture.

## Documentation

- [Architecture](./docs/architecture.md)
- [Setup Guide](./docs/setup-guide.md)
- [Lessons Learned](./docs/lessons-learned.md)

## Progress

Track current work in [TODO.md](./TODO.md)

See [DECISIONS.md](./DECISIONS.md) for architectural decisions.
