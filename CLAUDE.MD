# CLAUDE.MD - Context-Aware Documentation

This file provides context and guidelines for Claude AI when working on this AWS Bedrock Agent project. The documentation is organized by folder structure, enabling context-specific updates.

---

## Project Overview

**Project Name**: AWS Bedrock Agent Implementation
**Purpose**: Build, deploy, and manage AI agents using AWS Bedrock with Claude models
**Main Features**:
- Multi-functional AI agents with action groups
- Knowledge base integration for RAG (Retrieval-Augmented Generation)
- Lambda-based custom actions
- Comprehensive monitoring and deployment automation

**Goals**:
- Create production-ready Bedrock agents
- Implement scalable agent architectures
- Maintain best practices for AI agent development
- Enable rapid iteration and testing

---

## Folder Structure Strategy

This project follows a **feature-based folder structure** where each directory represents a specific aspect of the AWS Bedrock Agent ecosystem. Each folder has its own context, purpose, and update strategy.

### 📂 Project Structure Overview

```
/
├── agents/                    # Agent configurations and definitions
│   ├── configurations/        # Agent config files (JSON/YAML)
│   ├── instructions/          # Agent instruction templates
│   └── aliases/              # Agent alias definitions
│
├── lambda/                    # AWS Lambda functions for actions
│   ├── action-groups/        # Action group Lambda functions
│   ├── layers/               # Lambda layers for shared dependencies
│   └── shared/               # Shared utilities and helpers
│
├── knowledge-base/            # Knowledge base documents and data
│   ├── documents/            # Source documents (PDF, TXT, MD)
│   └── embeddings/           # Embedding configurations
│
├── schemas/                   # API and validation schemas
│   ├── openapi/              # OpenAPI 3.0 schemas for action groups
│   └── validation/           # Input/output validation schemas
│
├── docs/                      # Project documentation
│   ├── architecture/         # Architecture decisions and diagrams
│   ├── guides/               # How-to guides and tutorials
│   └── api/                  # API documentation
│
├── scripts/                   # Automation and utility scripts
│   ├── setup/                # Setup and initialization scripts
│   ├── deployment/           # Deployment automation
│   └── monitoring/           # Monitoring setup scripts
│
├── tests/                     # Test suites
│   ├── unit/                 # Unit tests for Lambda functions
│   ├── integration/          # Integration tests for agents
│   └── e2e/                  # End-to-end agent testing
│
├── monitoring/                # Monitoring and observability
│   ├── dashboards/           # CloudWatch dashboard configs
│   └── alerts/               # Alert and alarm configurations
│
├── config/                    # Environment configurations
│   ├── dev/                  # Development environment
│   ├── staging/              # Staging environment
│   └── prod/                 # Production environment
│
└── .claude/                   # Claude Code configurations
```

---

## Technology Stack

- **Cloud Platform**: AWS (Bedrock, Lambda, S3, CloudWatch)
- **AI Models**: Anthropic Claude (Sonnet, Haiku, Opus)
- **Languages**: Python 3.11+ (Lambda), Bash (scripts)
- **IaC**: AWS CDK / CloudFormation / Terraform
- **Vector Database**: Amazon OpenSearch Serverless
- **API Schema**: OpenAPI 3.0
- **Testing**: pytest, moto, boto3

---

## Folder-Specific Context

### 🤖 `/agents/` - Agent Configurations

**Purpose**: Store agent definitions, configurations, and metadata

**Context Update Strategy**:
- When updating agent instructions → modify files in `agents/instructions/`
- When creating new agents → add configuration in `agents/configurations/`
- When managing versions → update `agents/aliases/`

**File Conventions**:
- Configuration files: `{agent-name}-config.json`
- Instruction files: `{agent-name}-instructions.md`
- Alias files: `{agent-name}-{alias}.json`

**When to Update CLAUDE.MD**:
- New agent type added
- Agent architecture changes
- New instruction patterns established

---

### ⚡ `/lambda/` - Lambda Functions

**Purpose**: Action group implementations and custom logic

**Context Update Strategy**:
- When adding action groups → create new function in `lambda/action-groups/`
- When sharing code → add to `lambda/shared/`
- When adding dependencies → create layer in `lambda/layers/`

**File Conventions**:
- Function structure: `{action-group-name}/handler.py`, `requirements.txt`, `README.md`
- Shared modules: `lambda/shared/{module-name}.py`
- Layers: `lambda/layers/{layer-name}/python/`

**When to Update CLAUDE.MD**:
- New action group pattern introduced
- Shared utility added
- Lambda architecture changes

---

### 📚 `/knowledge-base/` - Knowledge Sources

**Purpose**: Store documents and embedding configurations for RAG

**Context Update Strategy**:
- When adding documents → place in `knowledge-base/documents/{category}/`
- When updating embeddings → modify configs in `knowledge-base/embeddings/`
- Organize by domain/category for better retrieval

**File Conventions**:
- Documents: Any format (PDF, TXT, MD, DOCX, HTML)
- Naming: descriptive names with version if applicable
- Embeddings: `{kb-name}-embedding-config.json`

**When to Update CLAUDE.MD**:
- New knowledge domain added
- Chunking strategy changes
- Embedding model updates

---

### 📋 `/schemas/` - API Schemas

**Purpose**: Define action group APIs and validation rules

**Context Update Strategy**:
- When creating action groups → add OpenAPI schema in `schemas/openapi/`
- When adding validation → create schemas in `schemas/validation/`
- Version schemas when making breaking changes

**File Conventions**:
- OpenAPI schemas: `{action-group-name}-api.yaml`
- Validation schemas: `{function-name}-validation.json`
- Include version in filename for major changes

**When to Update CLAUDE.MD**:
- New API pattern established
- Validation strategy changes
- Schema conventions updated

---

### 📖 `/docs/` - Documentation

**Purpose**: Project documentation, guides, and architecture decisions

**Context Update Strategy**:
- When documenting architecture → add to `docs/architecture/`
- When creating guides → add to `docs/guides/`
- When documenting APIs → add to `docs/api/`

**File Conventions**:
- Architecture: ADR (Architecture Decision Records) format
- Guides: Step-by-step markdown files
- API docs: Generated from OpenAPI schemas + manual additions

**When to Update CLAUDE.MD**:
- Major architectural changes
- New development patterns
- Documentation structure changes

---

### 🔧 `/scripts/` - Automation Scripts

**Purpose**: Setup, deployment, and maintenance automation

**Context Update Strategy**:
- When adding setup steps → create script in `scripts/setup/`
- When automating deployment → add to `scripts/deployment/`
- When adding monitoring → create in `scripts/monitoring/`

**File Conventions**:
- Bash scripts: `{purpose}.sh` with execute permissions
- Python scripts: `{purpose}.py` with shebang
- Include README.md explaining script usage

**When to Update CLAUDE.MD**:
- New deployment strategy
- Setup process changes
- Automation patterns updated

---

### 🧪 `/tests/` - Test Suites

**Purpose**: Automated testing for quality assurance

**Context Update Strategy**:
- When testing Lambda functions → add to `tests/unit/`
- When testing agent interactions → add to `tests/integration/`
- When testing full workflows → add to `tests/e2e/`

**File Conventions**:
- Test files: `test_{component}.py`
- Fixtures: `conftest.py` in each test directory
- Test data: `tests/fixtures/{test-data}/`

**When to Update CLAUDE.MD**:
- Testing strategy changes
- New test patterns introduced
- CI/CD integration updates

---

### 📊 `/monitoring/` - Observability

**Purpose**: Monitoring, logging, and alerting configurations

**Context Update Strategy**:
- When creating dashboards → add to `monitoring/dashboards/`
- When setting up alerts → add to `monitoring/alerts/`
- Use Infrastructure as Code for reproducibility

**File Conventions**:
- Dashboards: `{dashboard-name}-dashboard.json`
- Alerts: `{alert-name}-alarm.json`
- Include CloudWatch query samples

**When to Update CLAUDE.MD**:
- New metrics added
- Alerting strategy changes
- Dashboard conventions updated

---

### ⚙️ `/config/` - Environment Configurations

**Purpose**: Environment-specific settings and variables

**Context Update Strategy**:
- Separate configurations by environment (dev/staging/prod)
- Never commit secrets (use AWS Secrets Manager)
- Use .env.example files as templates

**File Conventions**:
- Config files: `{service}-config.{env}.json`
- Environment templates: `.env.{env}.example`
- Secrets references: Document in README, not in files

**When to Update CLAUDE.MD**:
- New environment added
- Configuration structure changes
- Secret management strategy updates

---

## Development Guidelines

### Code Style

**Python (Lambda Functions)**:
- Follow PEP 8 style guide
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use black for formatting, pylint for linting
- Docstrings: Google style

**Bash Scripts**:
- Use shellcheck for validation
- Include error handling (`set -euo pipefail`)
- Add usage documentation in comments
- Make scripts idempotent where possible

**YAML/JSON**:
- 2-space indentation
- Validate against schemas
- Use comments for complex configurations

### Best Practices

**Agent Development**:
- Write clear, specific agent instructions
- Include examples in agent prompts
- Test agents with diverse inputs
- Version control all configurations
- Use guardrails to prevent misuse

**Lambda Functions**:
- Keep functions small and focused
- Handle errors gracefully with proper status codes
- Log all invocations and errors
- Optimize for cold starts (<500ms)
- Use Lambda layers for shared dependencies

**Security**:
- Use least privilege IAM policies
- Never commit credentials or secrets
- Validate all inputs in Lambda functions
- Enable CloudTrail for audit logging
- Implement guardrails for agent safety
- Encrypt sensitive data in transit and at rest

**Knowledge Bases**:
- Organize documents by domain/category
- Keep documents up-to-date
- Use consistent formatting
- Test retrieval quality regularly
- Monitor chunking effectiveness

**Testing**:
- Write tests before deploying to production
- Test edge cases and error scenarios
- Use mocking for external dependencies
- Maintain >80% code coverage for Lambda functions
- Test agent conversations end-to-end

---

## Context-Aware Update Protocol

### How This File Gets Updated

When Claude is asked to work on different aspects of the project, CLAUDE.MD should be updated based on the **folder context**:

#### 1️⃣ **Agent-Related Updates** (`/agents/`)
**Triggers**:
- "Update agent instructions for..."
- "Create new agent configuration..."
- "Add agent alias..."

**Update Sections**:
- `/agents/` folder context
- Agent Development best practices
- Common Tasks → Agent Management

#### 2️⃣ **Lambda-Related Updates** (`/lambda/`)
**Triggers**:
- "Create new action group..."
- "Add Lambda function..."
- "Update shared utilities..."

**Update Sections**:
- `/lambda/` folder context
- Lambda Functions best practices
- Technology Stack (if new dependencies)

#### 3️⃣ **Knowledge Base Updates** (`/knowledge-base/`)
**Triggers**:
- "Add documents to knowledge base..."
- "Update embedding configuration..."
- "Reorganize knowledge sources..."

**Update Sections**:
- `/knowledge-base/` folder context
- Knowledge Bases best practices
- Architecture (if KB structure changes)

#### 4️⃣ **Schema Updates** (`/schemas/`)
**Triggers**:
- "Create OpenAPI schema..."
- "Add validation rules..."
- "Update API definition..."

**Update Sections**:
- `/schemas/` folder context
- API Schema conventions
- Development Guidelines

#### 5️⃣ **Documentation Updates** (`/docs/`)
**Triggers**:
- "Add architecture documentation..."
- "Create guide for..."
- "Document API..."

**Update Sections**:
- `/docs/` folder context
- Resources section
- Project Overview (if major changes)

#### 6️⃣ **Script Updates** (`/scripts/`)
**Triggers**:
- "Create deployment script..."
- "Add setup automation..."
- "Automate monitoring..."

**Update Sections**:
- `/scripts/` folder context
- Setup and Installation
- Building/Deployment

#### 7️⃣ **Test Updates** (`/tests/`)
**Triggers**:
- "Add unit tests..."
- "Create integration tests..."
- "Test agent end-to-end..."

**Update Sections**:
- `/tests/` folder context
- Testing best practices
- Testing section

#### 8️⃣ **Monitoring Updates** (`/monitoring/`)
**Triggers**:
- "Create CloudWatch dashboard..."
- "Add alerts for..."
- "Set up monitoring..."

**Update Sections**:
- `/monitoring/` folder context
- Best Practices → Monitoring
- Common Tasks → Monitoring

#### 9️⃣ **Configuration Updates** (`/config/`)
**Triggers**:
- "Add environment config..."
- "Update settings for..."
- "Configure for production..."

**Update Sections**:
- `/config/` folder context
- Setup and Installation
- Environment-specific notes

---

## Setup and Installation

### Prerequisites
```bash
# AWS CLI
aws --version  # Should be >= 2.0

# Python
python --version  # Should be >= 3.11

# Node.js (optional, for CDK)
node --version  # Should be >= 18.0
```

### Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd MyFirstRepo

# Run setup script
./scripts/setup/initialize.sh

# Configure AWS credentials
aws configure

# Set up development environment
./scripts/setup/dev-environment.sh
```

### AWS Configuration
```bash
# Verify AWS access
aws sts get-caller-identity

# Check Bedrock model access
aws bedrock list-foundation-models --region us-east-1

# Create necessary IAM roles
./scripts/setup/create-iam-roles.sh
```

---

## Running the Project

### Local Development
```bash
# Test Lambda functions locally
cd lambda/action-groups/{function-name}
python handler.py

# Validate schemas
./scripts/validation/validate-schemas.sh

# Run tests
pytest tests/
```

### Deploy Agent
```bash
# Deploy to development
./scripts/deployment/deploy.sh dev

# Deploy to production
./scripts/deployment/deploy.sh prod
```

### Test Agent
```bash
# Test via AWS Console
# Navigate to Bedrock > Agents > [Your Agent] > Test

# Test via CLI
aws bedrock-agent-runtime invoke-agent \
  --agent-id <agent-id> \
  --agent-alias-id <alias-id> \
  --session-id test-session \
  --input-text "Hello, who are you?"
```

---

## Testing

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_lambda_handler.py

# Run with coverage
pytest tests/unit/ --cov=lambda --cov-report=html
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/ -v

# Test specific agent
pytest tests/integration/test_agent_actions.py
```

### End-to-End Tests
```bash
# Run E2E tests
pytest tests/e2e/ -v --slow

# Test production agent
pytest tests/e2e/test_production_agent.py
```

---

## Building/Deployment

### Build Lambda Packages
```bash
# Build all Lambda functions
./scripts/deployment/build-lambdas.sh

# Build specific function
./scripts/deployment/build-lambda.sh action-groups/get-order-status
```

### Deploy Infrastructure
```bash
# Deploy using CDK (if applicable)
cdk deploy --all

# Deploy using CloudFormation
./scripts/deployment/deploy-cfn.sh

# Deploy using Terraform
terraform apply -var-file=config/prod/terraform.tfvars
```

### Deploy Agent
```bash
# Create/update agent
./scripts/deployment/deploy-agent.sh prod

# Create agent alias
./scripts/deployment/create-alias.sh prod v1
```

---

## Important Notes for Claude

### Folder Context Awareness
- **Always determine which folder context applies** before making updates
- When working in a specific folder, update the relevant section of CLAUDE.MD
- Maintain consistency with established patterns in each folder
- Cross-reference related folders when changes affect multiple areas

### Preferred Approaches

**For Agent Instructions**:
- Be specific and directive, not suggestive
- Include examples of desired behavior
- Define clear boundaries and limitations
- Specify tone, style, and response format

**For Lambda Functions**:
- Keep functions under 50 lines when possible
- Extract shared logic to `lambda/shared/`
- Always include error handling
- Log at appropriate levels (INFO, WARNING, ERROR)

**For Documentation**:
- Update docs when code changes
- Include examples and use cases
- Keep architecture docs current
- Document "why" not just "what"

**For Schemas**:
- Validate before committing
- Include detailed descriptions
- Version breaking changes
- Keep examples in schemas

### Areas Needing Special Attention

**Security**:
- All Lambda functions must validate inputs
- Never log sensitive information
- Use AWS Secrets Manager for credentials
- Implement guardrails for agents

**Performance**:
- Monitor Lambda cold starts
- Optimize knowledge base chunking
- Cache when appropriate
- Use appropriate model for use case

**Cost Management**:
- Monitor token usage
- Use Haiku for simple tasks
- Implement session timeouts
- Clean up unused resources

**Reliability**:
- Implement retry logic with exponential backoff
- Handle rate limits gracefully
- Test failure scenarios
- Monitor error rates

---

## Common Tasks

### Create New Agent
```bash
# 1. Create configuration
./scripts/agents/create-agent-config.sh "AgentName"

# 2. Write instructions
nano agents/instructions/agent-name-instructions.md

# 3. Deploy
./scripts/deployment/deploy-agent.sh dev
```

### Add Action Group
```bash
# 1. Create Lambda function
./scripts/lambda/create-action-group.sh "ActionGroupName"

# 2. Create OpenAPI schema
nano schemas/openapi/action-group-name-api.yaml

# 3. Update agent configuration
./scripts/agents/add-action-group.sh "AgentName" "ActionGroupName"
```

### Update Knowledge Base
```bash
# 1. Add documents
cp documents/*.pdf knowledge-base/documents/category/

# 2. Sync knowledge base
./scripts/knowledge-base/sync-kb.sh "KnowledgeBaseName"

# 3. Test retrieval
./scripts/knowledge-base/test-kb.sh "test query"
```

### Monitor Agent
```bash
# View recent logs
./scripts/monitoring/view-logs.sh "AgentName"

# Check metrics
./scripts/monitoring/check-metrics.sh "AgentName"

# View dashboard
./scripts/monitoring/open-dashboard.sh "AgentName"
```

---

## Resources

### AWS Documentation
- [Amazon Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Amazon Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/)
- [Claude Models on Bedrock](https://docs.anthropic.com/claude/docs/claude-on-amazon-bedrock)

### Internal Documentation
- [AWS Bedrock Agent Plan](./AWS_BEDROCK_AGENT_PLAN.md)
- [Architecture Decisions](./docs/architecture/)
- [API Documentation](./docs/api/)
- [Development Guides](./docs/guides/)

### Tools & Libraries
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CDK](https://docs.aws.amazon.com/cdk/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [pytest Documentation](https://docs.pytest.org/)

---

## Version History

| Version | Date | Changes | Updated Sections |
|---------|------|---------|------------------|
| 1.0.0 | 2026-01-09 | Initial folder-aware CLAUDE.MD | All sections |

---

## How to Use This File

### For Developers
1. Read relevant folder sections before working in that area
2. Follow established conventions and patterns
3. Update this file when introducing new patterns
4. Reference this file during code reviews

### For Claude AI
1. **Check folder context** when receiving requests
2. **Update relevant sections** after making changes
3. **Maintain consistency** with established patterns
4. **Cross-reference** related sections when changes span multiple folders
5. **Version updates** in the Version History table

### For Project Managers
1. Use this as a project structure reference
2. Understand folder organization
3. Track architectural decisions
4. Plan resource allocation based on folder organization

---

**Last Updated**: 2026-01-09
**Maintained By**: Claude AI + Development Team
**Update Frequency**: On every significant folder/pattern change
