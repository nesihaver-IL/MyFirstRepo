# Command Registry
# Auto-generated list of available slash commands

## Available Commands

### Full Command Names

#### Core Workflow (use in order)
- exploration-phase
- create-plan
- execute-plan
- review
- peer-review
- update-docs

#### Project Management
- create-issue

#### Cloud Platforms
- azure-ai-foundry
- aws-strands
- aws-agentcore
- terraform-ops

#### Domain Skills (added 2026-02-27)
- streamlit-dash
- data-pipeline
- jira-confluence

#### Quality & Security (added 2026-02-27)
- test-runner
- security-audit

#### Design & Utilities
- figma
- analytics-metrics
- copilot-docs
- nano-banana-pro
- github-trending

### Aliases (Short Names)
You can use these trigger phrases to activate commands:

| Alias/Trigger | Full Command | Description |
|---------------|--------------|-------------|
| "create issue" | create-issue | Document bugs, features, ideas |
| "log bug" | create-issue | Record a bug |
| "track feature" | create-issue | Track new feature |
| "explore" | exploration-phase | Understand task and code |
| "explore codebase" | exploration-phase | Analyze existing code |
| "understand task" | exploration-phase | Clarify requirements |
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
| "tfstate" | terraform-ops | Inspect Terraform state |
| "infrastructure" | terraform-ops | AWS infrastructure management |
| "deploy aws" | terraform-ops | Deploy Lambda + DynamoDB + API GW |
| "streamlit" | streamlit-dash | Garmin analytics dashboard (01-personal/) |
| "run dashboard" | streamlit-dash | Launch or update Streamlit app |
| "garmin analytics" | streamlit-dash | Update health metrics dashboard |
| "ingest data" | data-pipeline | Garmin data ingestion + ETL |
| "pipeline" | data-pipeline | Data pipeline operations |
| "migrate dataset" | data-pipeline | Move files to data/raw/ |
| "garmin data" | data-pipeline | Garmin JSON export management |
| "rag dataset" | data-pipeline | Update RAG ZIP batches |
| "jira ticket" | jira-confluence | Create or update JIRA issue |
| "confluence page" | jira-confluence | Create or update Confluence page |
| "jira automation" | jira-confluence | Build JIRA automation workflow |
| "update board" | jira-confluence | Read/update JIRA sprint board |
| "run tests" | test-runner | Execute pytest across projects |
| "pytest" | test-runner | Run Python test suite |
| "test coverage" | test-runner | Check test coverage report |
| "validate tests" | test-runner | Verify tests before commit |
| "security scan" | security-audit | Scan for secrets + OWASP issues |
| "check secrets" | security-audit | Detect hardcoded credentials |
| "audit credentials" | security-audit | Verify no secrets in code |
| "owasp" | security-audit | OWASP Top 10 compliance check |
| "dashboard" | analytics-metrics | Data visualization / Recharts charts |
| "chart" | analytics-metrics | KPI displays, metrics dashboards |
| "copilot" | copilot-docs | GitHub Copilot custom instructions |
| "figma" | figma | Figma API, design tokens, component gen |
| "generate image" | nano-banana-pro | Gemini 3 Pro image generation |
| "trending" | github-trending | GitHub trending repos discovery |

## Usage Examples

### Short Form (Using Triggers)
```
"explore the authentication system"
→ Triggers: exploration-phase

"create issue - login button broken"
→ Triggers: create-issue

"review the shopping cart code"
→ Triggers: review

"terraform plan the garmin backend changes"
→ Triggers: terraform-ops

"run the garmin backend tests"
→ Triggers: test-runner

"scan for secrets before I commit"
→ Triggers: security-audit

"update the streamlit dashboard charts"
→ Triggers: streamlit-dash
```

### Direct Invocation (Claude Code)
```
Use the terraform-ops skill to plan infra changes
Use the test-runner skill to validate before PR
Use the security-audit skill to gate this commit
Use the streamlit-dash skill to update the dashboard
Use the data-pipeline skill to migrate garmin files
Use the jira-confluence skill to create the sprint ticket
```

### Cursor IDE
```
/create-issue
/exploration-phase
/create-plan
/execute-plan
/review
/peer-review
/update-docs
/terraform-ops
/test-runner
/security-audit
/streamlit-dash
/data-pipeline
/jira-confluence
```

## Auto-Loading

### Claude Code
Commands in `.claude/skills/` are **automatically loaded** on startup.
No configuration needed!

### Cursor IDE
Commands in `.cursor/commands/` are **automatically detected** when you type `/`.

## Troubleshooting

### "Unknown slash command" Error

**Problem**: Typed `/create` instead of `/create-issue`

**Solutions**:
1. Use the full command name: `/create-issue`
2. Or use natural language: "create an issue for this bug"
3. Check available commands: See list above

### Commands Not Showing Up

**Claude Code**:
- Restart Claude Code
- Verify files exist in `.claude/skills/*/SKILL.md`
- Check YAML frontmatter has `name:` field

**Cursor IDE**:
- Restart Cursor
- Type `/` to see all commands
- Verify files exist in `.cursor/commands/*.md`

## Agents (Sub-Agent Specs)

Domain-specialized agents for complex delegated tasks.
Located in `.claude/agents/*/AGENT.md`.

| Agent | Scope | Use When |
|-------|-------|---------|
| `garmin-health-agent` | `01-personal/garmin-health/` | Health analytics, training analysis, athlete coaching |
| `aws-infra-agent` | `garmin-health/backend/` + `aws-ai-agent/` | Terraform, Lambda, DynamoDB, IAM operations |
| `jira-confluence-agent` | `02-work/automation-integrations/` | JIRA/Confluence automation, sprint workflows |
| `code-quality-agent` | All projects | Pre-PR quality gate, security scan, test validation |

### Invoking Agents
```
"Garmin health agent: analyze my last month of training"
"AWS infra agent: check why the Lambda is failing"
"JIRA agent: build the sprint review automation"
"Quality agent: run the full pre-PR check"
```

## Diagnostic Scripts

| Script | Purpose |
|--------|---------|
| `.claude/scripts/check-connectivity.sh` | Test internet, Anthropic API, CLI install, and auth |
| `.claude/scripts/check-connectivity.bat` | Same as above, for Windows |

Run before reporting login or connectivity issues.

## Command Status

Last Updated: 2026-02-27
Total Skills: 20
Total Agents: 4
Status: ✅ Active
