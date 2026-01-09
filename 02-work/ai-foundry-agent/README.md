# AI Foundry Agent

Enterprise AI agent built on Azure AI Foundry.

## Features

- [ ] Core agent with Azure OpenAI
- [ ] JIRA integration
- [ ] Confluence integration
- [ ] Vector search for knowledge base
- [ ] REST API endpoints

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure Azure
az login
az account set --subscription <subscription-id>

# Run locally
python -m src.api.main
```

## Architecture

See [docs/architecture.md](./docs/architecture.md) for detailed architecture.

## Documentation

- [Architecture](./docs/architecture.md)
- [API Specification](./docs/api-spec.md)
- [Runbooks](./docs/runbooks/)
- [Onboarding](./docs/onboarding.md)

## Status

See [STATUS.md](./STATUS.md) for current sprint status.

## Decisions

See [DECISIONS.md](./DECISIONS.md) for architectural decisions.
