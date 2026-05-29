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
│   ├── setup/          # GUIDED-SETUP-CHECKLIST, QUICKSTART-WINDOWS, IMAGE_PROCESSING_SETUP
│   ├── operations/     # monitoring-guide, production-checklist, document-management
│   └── runbooks/       # deployment, incident-response, scaling
├── scripts/
│   └── windows/        # All .bat and .ps1 deployment/setup scripts
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

## Windows Setup & Deployment
All Windows scripts are in `scripts/windows/`:
```powershell
# First-time setup
scripts\windows\setup-windows.ps1

# Deploy infrastructure
scripts\windows\deploy-infrastructure.ps1

# Run agent
scripts\windows\run.ps1

# Test agent
scripts\windows\test-agent.bat
```
See `docs/setup/QUICKSTART-WINDOWS.md` for step-by-step guide.

## Claude Code Skills for This Project

| Skill | When to Use |
|-------|-----------|
| `azure-ai-foundry` | Building agent flows, model invocation, prompt testing |
| `test-runner` | Running pytest suite before commit |
| `security-audit` | Scanning secrets, OWASP issues before PR |
| `jira-confluence` | Creating tickets, syncing documentation |
| `review` | Self-reviewing code for bugs |

## Team Requirements

- All PRs require code review
- Follow semantic versioning
- Update `STATUS.md` on sprint changes
- Document decisions in `DECISIONS.md`
- Run `security-audit` and `test-runner` before creating PR

## Important Notes

- **Secrets management**: Use Azure Key Vault (never hardcode credentials)
- **Logging**: All external API calls must be logged (includes timestamps, method, response code)
- **Error handling**: All integrations must implement retry logic with exponential backoff
- **Security**: Follow least privilege principle for Azure service accounts
- **Monitoring**: Set up Application Insights alerts for production agent

## Configuration

### Local Development (.env)
```bash
AZURE_SUBSCRIPTION_ID=<your-sub-id>
AZURE_RESOURCE_GROUP=<resource-group-name>
AZURE_KEY_VAULT_NAME=<vault-name>
OPENAI_API_KEY=<loaded from Key Vault>
JIRA_API_TOKEN=<loaded from Key Vault>
CONFLUENCE_API_TOKEN=<loaded from Key Vault>
```

### Windows Deployment
```powershell
# Setup
scripts\windows\setup-windows.ps1

# Deploy
scripts\windows\deploy-infrastructure.ps1

# Run locally
scripts\windows\run.ps1

# Test
scripts\windows\test-agent.bat
```

See `docs/setup/QUICKSTART-WINDOWS.md` for step-by-step guide.

## Monitoring & Operations

- **Application Insights**: Track agent latency, error rates, dependency failures
- **Azure Monitor**: Alert on quota exhaustion (OpenAI, Semantic Kernel)
- **Logs**: All agent actions logged to Azure Log Analytics
- **Incident Response**: See `docs/runbooks/incident-response.md`

## Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Semantic Kernel Documentation](https://learn.microsoft.com/semantic-kernel/)
- [Azure Key Vault Best Practices](https://learn.microsoft.com/azure/key-vault/general/best-practices)
- [Application Insights Guide](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
