# Onboarding Guide - AI Foundry Agent

Welcome to the AI Foundry Agent project! This guide will help you get started.

## Prerequisites

- Azure subscription access (request via IT)
- Python 3.11+
- Azure CLI
- VS Code with Python extension

## Day 1: Setup

### 1. Get Access

- [ ] Azure subscription access
- [ ] GitHub repository access
- [ ] JIRA project access
- [ ] Teams channel added

### 2. Local Setup

```bash
# Clone repository
git clone <repo-url>
cd ai-foundry-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Azure login
az login
```

### 3. Environment Configuration

Create `.env` file from template:
```bash
cp .env.example .env
# Edit .env with your values
```

## Day 2-3: Understanding the Codebase

### Read These First

1. [Architecture](./architecture.md) - High-level system design
2. [API Spec](./api-spec.md) - API endpoints
3. Project `CLAUDE.md` - Development guidelines
4. `DECISIONS.md` - Past architectural decisions

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/agent/` | Core agent logic |
| `src/integrations/` | External service connectors |
| `src/api/` | REST API endpoints |
| `tests/` | Test suites |

## Day 4-5: First Contribution

### Recommended First Tasks

- [ ] Fix a small bug
- [ ] Add a unit test
- [ ] Improve documentation

### Development Workflow

1. Create feature branch
2. Make changes
3. Run tests: `pytest`
4. Create PR
5. Request review

## Questions?

- **Technical**: Check `#ai-foundry-dev` Teams channel
- **Process**: Ask team lead
- **Access**: Contact IT
