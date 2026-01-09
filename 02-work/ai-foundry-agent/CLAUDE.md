# CLAUDE.md - AI Foundry Agent

## Project Overview

Enterprise AI agent built on Azure AI Foundry for internal business operations.

## Technology Stack

- **Language**: Python 3.11+
- **AI Platform**: Azure AI Foundry (formerly AI Studio)
- **Framework**: Semantic Kernel / LangChain
- **Vector Store**: Azure AI Search
- **Infrastructure**: Azure Resource Manager (Bicep)

## Project Structure

```
ai-foundry-agent/
├── src/
│   ├── agent/          # Core agent logic
│   ├── integrations/   # JIRA, Confluence, etc.
│   ├── vector-store/   # RAG implementation
│   └── api/            # REST API endpoints
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
└── environments/
```

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Azure login
az login

# Run locally
python -m src.api.main
```

## Team Requirements

- All PRs require code review
- Follow semantic versioning
- Update STATUS.md on sprint changes
- Document decisions in DECISIONS.md

## Important Notes

- Use Azure Key Vault for secrets
- Follow company security policies
- All integrations must have retry logic
- Log all external API calls

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel/)
