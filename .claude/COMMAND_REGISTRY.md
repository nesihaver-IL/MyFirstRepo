# Command Registry
# Available slash commands - 26 active skills, 4 agents

## Available Commands

### Full Command Names

#### Core Workflow (use in order)
- create-plan
- execute-plan
- review
- peer-review
- update-docs

#### Project Management
- create-issue

#### Cloud Platforms
- azure-ai-foundry
- aws-bedrock
- aws-strands
- aws-agentcore
- aws-step-functions
- aws-lambda
- terraform-ops

#### Domain Skills
- streamlit-dash
- data-pipeline
- garmin-analyzer
- jira-confluence

#### Quality & Security
- test-runner
- security-audit

#### Presentation & Design
- slide-authoring
- create-slide
- create-theme
- apply-comments
- current-slide
- html-sync
- analytics-metrics

### Aliases (Short Names)

| Alias/Trigger | Full Command | Description |
|---------------|--------------|-------------|
| "create issue" | create-issue | Document bugs, features, ideas |
| "log bug" | create-issue | Record a bug |
| "track feature" | create-issue | Track new feature |
| "plan" | create-plan | Create implementation plan |
| "make plan" | create-plan | Design solution |
| "implement plan" | execute-plan | Write the code |
| "build" | execute-plan | Execute implementation |
| "review" | review | Self-review code |
| "check code" | review | Find bugs and issues |
| "peer review" | peer-review | Multi-perspective review |
| "second opinion" | peer-review | Get fresh perspective |
| "docs" | update-docs | Update documentation |
| "update docs" | update-docs | Sync documentation |
| "azure ai" | azure-ai-foundry | Azure AI Foundry tasks (02-work/) |
| "azure foundry" | azure-ai-foundry | Azure AI Studio / Prompt Flow |
| "aws agent" | aws-strands | AWS model-agnostic agent (01-personal/) |
| "strands" | aws-strands | Strands Agents SDK ReAct patterns |
| "bedrock agent" | aws-agentcore | AWS Bedrock AgentCore (01-personal/) |
| "agentcore" | aws-agentcore | Lambda tools, Bedrock orchestration |
| "terraform plan" | terraform-ops | Plan infra changes (garmin + aws-ai-agent) |
| "deploy infra" | terraform-ops | Apply Terraform (always plan first) |
| "infrastructure" | terraform-ops | AWS infrastructure management |
| "streamlit" | streamlit-dash | Garmin analytics dashboard (01-personal/) |
| "run dashboard" | streamlit-dash | Launch or update Streamlit app |
| "garmin analytics" | streamlit-dash | Update health metrics dashboard |
| "ingest data" | data-pipeline | Garmin data ingestion + ETL |
| "pipeline" | data-pipeline | Data pipeline operations |
| "garmin data" | data-pipeline | Garmin JSON export management |
| "analyze training" | garmin-analyzer | Garmin training data analysis |
| "garmin report" | garmin-analyzer | Generate health/fitness report |
| "jira ticket" | jira-confluence | Create or update JIRA issue |
| "confluence page" | jira-confluence | Create or update Confluence page |
| "jira automation" | jira-confluence | Build JIRA automation workflow |
| "run tests" | test-runner | Execute pytest across projects |
| "pytest" | test-runner | Run Python test suite |
| "test coverage" | test-runner | Check test coverage report |
| "security scan" | security-audit | Scan for secrets + OWASP issues |
| "check secrets" | security-audit | Detect hardcoded credentials |
| "owasp" | security-audit | OWASP Top 10 compliance check |
| "dashboard" | analytics-metrics | Data visualization / Recharts charts |
| "chart" | analytics-metrics | KPI displays, metrics dashboards |
| "bedrock model" | aws-bedrock | Invoke Bedrock foundational models |
| "knowledge base" | aws-bedrock | Bedrock KB RAG retrieval + ingestion |
| "bedrock flows" | aws-bedrock | Visual agentic flow builder |
| "converse api" | aws-bedrock | Bedrock Converse API + tool use |
| "state machine" | aws-step-functions | Step Functions state machine design |
| "step functions" | aws-step-functions | Orchestrate agentic pipelines |
| "lambda tool" | aws-lambda | Lambda as Bedrock agent tool backend |
| "lambda handler" | aws-lambda | Serverless function patterns |
| "function url" | aws-lambda | Lambda HTTP endpoint for agents |
| "create slide" | create-slide | Add a new slide to the active deck |
| "new slide" | create-slide | Create a slide with layout + content |
| "set theme" | create-theme | Apply or create a deck theme |
| "current slide" | current-slide | Show the active/focused slide |
| "apply comments" | apply-comments | Apply review comments to slides |
| "html sync" | html-sync | Sync HTML deck to disk |

## Usage Examples

```
"create issue - login button broken"       -> create-issue
"plan the garmin data migration"           -> create-plan
"review the analytics module"              -> review
"terraform plan the garmin backend"        -> terraform-ops
"run tests before PR"                      -> test-runner
"scan for secrets before I commit"         -> security-audit
"update the streamlit dashboard charts"    -> streamlit-dash
"analyze my training data"                 -> garmin-analyzer
"create a JIRA ticket for this bug"        -> jira-confluence
```

## Agents (Sub-Agent Specs)

Domain-specialized agents for complex delegated tasks.
Located in `.claude/agents/*/AGENT.md`.

| Agent | Scope | Use When |
|-------|-------|---------|
| `garmin-health-agent` | `01-personal/garmin-health/` | Health analytics, training analysis, athlete coaching |
| `aws-infra-agent` | `garmin-health/backend/` + `aws-ai-agent/` | Terraform, Lambda, DynamoDB, IAM operations |
| `jira-confluence-agent` | `02-work/automation-integrations/` | JIRA/Confluence automation, sprint workflows |
| `code-quality-agent` | All projects | Pre-PR quality gate, security scan, test validation |

## Archived Skills

Moved to `.claude/skills-archive/` - restore to `skills/` if needed:
`exploration-phase`, `resume-optimizer`, `cyber-exec-brief`, `pptx-builder`, `excel-pm-planner`, `aws-eventbridge`, `figma`, `copilot-docs`, `nano-banana-pro`, `github-trending`, `content-to-reference`, `google-workspace-cli`, `xlsx`

## Diagnostic Scripts

| Script | Purpose |
|--------|---------|
| `.claude/scripts/check-connectivity.sh` | Test internet, Anthropic API, CLI install, and auth |
| `.claude/scripts/check-connectivity.bat` | Same as above, for Windows |

## Status

Last Updated: 2026-07-04
Total Active Skills: 26
Total Archived Skills: 13
Total Agents: 4
