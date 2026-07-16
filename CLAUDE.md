# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Workspace Overview

This is a sophisticated multi-project workspace for AI agent development, containing:
- **Personal projects** (`01-personal/`) for learning and experimentation with AWS Bedrock, data science, and utilities
- **Work projects** (`02-work/`) for professional deliverables using Azure AI Foundry and enterprise automation
- **Planning & research** (`03-plans/`) for strategy documents and technical roadmaps
- **Reference materials** (`04-reference/`) for knowledge base, cheatsheets, and archived data
- **Claude Code ecosystem** (`.claude/`) with skills and agents auto-loaded — see `.claude/COMMAND_REGISTRY.md` for the current count (36 skills, 4 agents as of 2026-07-16; don't hardcode a number here, it goes stale)

## Project Architecture Map

### Core Active Projects

| Project | Location | Stack | Purpose |
|---------|----------|-------|---------|
| **Garmin Health** | `01-personal/garmin-health/` | Python, AWS Lambda, Terraform, Streamlit | End-to-end health analytics system: Garmin data ingestion → DynamoDB → AI-powered dashboard |
| **AWS AI Agent** | `01-personal/aws-ai-agent/` | Python, AWS Bedrock, LangChain | Generic AWS Bedrock agent framework using Strands/AgentCore patterns |
| **Math Practice** | `01-personal/math-practice/` | Python, JavaScript | Grade 5 math exam generator with Hebrew UI |
| **Interview Coach** | `01-personal/interview-coach/` | JavaScript (Node submodule) | Career coaching skill and utility scripts |
| **Azure Foundry Agent** | `02-work/ai-foundry-agent/` | Python, Azure AI Foundry | Enterprise agent for professional use cases |
| **JIRA/Confluence Automation** | `02-work/automation-integrations/` | Python | Automation integrations for work ticketing systems |

### Other Project Folders (undocumented until 2026-07-16)

These exist in the work tree but were missing from the table above — added here rather than left
undocumented. Verify each is still active before treating it as such; several show no commits since
early-to-mid April 2026.

| Project | Location | Notes |
|---------|----------|-------|
| **Zohar Resume** | `01-personal/zohar-resume/` | Resume tooling |
| **Windows Monitor** | `01-personal/windows-monitor/` | System monitoring utility |
| **Bookmark Management** | `01-personal/bookmark-management/` | Bookmark tooling |
| **Electricity Dashboard** | `01-personal/electricity-dashboard/` | Gmail API bill extraction (see root TODO.md) |
| **Tzofim Payments** | `01-personal/tzofim-payments/` | Payments-related utility |
| **Strategy Presentation** | `02-work/strategy-presentation/` | Contains tracked `.xlsx` planning files |
| **AWS Cleanup** | `02-work/aws-cleanup/` | AWS account cleanup scripts |
| **Handoff** | `02-work/handoff/` | Handoff documentation/materials |

`sandbox` and `marketplace` were archived to `01-personal/archive/` on 2026-07-16 (idle since
2026-01-09 and 2026-02-17 respectively) rather than documented here.

### Architecture Highlights

**Garmin Health** (most complex):
- `backend/` — AWS Lambda (4 functions), Terraform infrastructure, OAuth flow, webhook handlers
- `analytics/` — Streamlit dashboard with Anthropic Claude integration, custom modules (`ai_insights`, `charts`, `data_loader`, `metrics`)
- `datasets/` — RAG vector datasets (activities, wellness, training)
- `data/{raw,processed,exports}/` — Runtime data layer (gitignored, user-supplied)

**AWS AI Agent** (framework):
- Clean separation of concerns — no domain logic, reusable patterns
- Bedrock model invocation, tool use, prompt management
- Terraform infrastructure for backend services

## Build, Test & Run Commands

### Python Projects (with `.venv`)

Before running any Python command, **always check for and activate the project's `.venv`**:

```bash
# Garmin Health Analytics (Streamlit dashboard)
cd 01-personal/garmin-health/analytics
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

# Garmin Health Backend (AWS Lambda)
cd 01-personal/garmin-health/backend
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/test.sh        # Run OAuth + query tests
bash scripts/deploy.sh      # Deploy Terraform
bash scripts/destroy.sh     # Tear down infrastructure

# Math Practice Tests
cd 01-personal/math-practice
python -m pytest tests/ -v

# AWS AI Agent (if venv exists)
cd 01-personal/aws-ai-agent
[if .venv exists: source .venv/bin/activate]
pip install -r requirements.txt  # or add to .venv
python run_agent.py
```

### JavaScript/Node Projects

```bash
# Interview Coach (submodule with build scripts)
cd 01-personal/interview-coach
npm install
npm run build    # or project-specific script

# Work projects
cd 02-work/automation-integrations
npm install && npm run test
```

### Terraform (Garmin Backend)

```bash
cd 01-personal/garmin-health/backend/terraform
terraform init
terraform plan -var-file="../config/terraform.tfvars"
terraform apply -var-file="../config/terraform.tfvars"
```

## Python Environment Rules

- **Before running `pip`, `python`, or any Python script, check for a project-level `.venv`**
- Use `.venv/bin/python` (not system `python3`) when a `.venv` exists
- If `.venv` exists: activate it (`source .venv/bin/activate`) before pip install
- Known project venvs:
  - `01-personal/garmin-health/analytics/.venv` — Streamlit + Anthropic SDK
  - `01-personal/aws-ai-agent/.venv` — Bedrock + LangChain (if exists)
- There is no root-level venv — each project is isolated
- When creating a new `.venv`: `python -m venv .venv && source .venv/bin/activate`

## Development Workflows

### When to Use Claude Code Skills

Use the skill system (invoke via natural language or slash commands):

| Goal | Skill(s) | Trigger Phrase |
|------|----------|----------------|
| Unfamiliar codebase → new feature | `exploration-phase` → `create-plan` → `execute-plan` | "explore the auth system" |
| Bug investigation & fix | `review` | "review this code for bugs" |
| High-stakes code changes | `peer-review` | "second opinion on this refactor" |
| Before every commit | `security-audit` | "scan for secrets before I commit" |
| Before every PR | `test-runner` + `security-audit` | "run tests and security check" |
| Garmin health work | `streamlit-dash` or `data-pipeline` or `garmin-analyzer` | "update the streamlit dashboard" |
| AWS infrastructure | `terraform-ops` + `aws-bedrock` + `aws-lambda` | "terraform plan the garmin backend" |
| Azure Foundry work | `azure-ai-foundry` | "build an agent in Azure AI Foundry" |
| JIRA/Confluence | `jira-confluence` | "create a JIRA ticket for this" |
| Docs after merge | `update-docs` | "update docs to reflect changes" |

### Domain-Specialized Agents

Delegate complex multi-step tasks to these agents (found in `.claude/agents/`):

```
"Garmin health agent: analyze my training data for the last month"
"AWS infra agent: plan the Lambda deployment for the analytics backend"
"JIRA agent: build the sprint automation workflow"
"Code quality agent: run the full pre-PR security and test gate"
```

## Global Coding Standards

### Code Style

- **Formatting**: Prettier (JavaScript/TypeScript), Black (Python)
- **Principles**: explicit > implicit, small focused functions, single responsibility
- Type hints and annotations where applicable
- Self-documenting code with clear variable and function names

### Documentation Standards

- Every project must have a `CLAUDE.md` with project-specific context
- Document architectural decisions in project-level `DECISIONS.md`
- Track active work in project-level `TODO.md`
- Use templates from `.config/templates/` for consistency

### Security & Testing

- Write tests for critical functionality (especially data pipelines, API handlers)
- No secrets in code: use `.env` files (excluded from git)
- Always run `security-audit` skill before committing
- All code must pass linting before merge

## Directory Conventions

| Directory | Purpose | Access | Notes |
|-----------|---------|--------|-------|
| `01-personal/` | Learning & experiments | Private | Master Garmin, AWS Bedrock, utilities |
| `02-work/` | Professional deliverables | May be shared | Azure AI Foundry, JIRA automation |
| `03-plans/` | Strategy, roadmaps, research | Private | Human-owned planning |
| `04-reference/` | Knowledge base, cheatsheets | Private | ChatGPT archives, learning materials |
| `.claude/` | Skills, agents, diagnostic tools | System | Auto-loaded by Claude Code |
| `.plans/` | Claude-generated execution plans | System | Created by `create-plan` skill |

## Git Workflow

### Commit Discipline

- **Timing**: Commit at logical milestones, not end-of-session dumps
- **Staging**: Stage specific files by name — never use `git add -A` blindly
- **Message format**: Use conventional prefixes:
  - `feat:` — new feature or capability
  - `fix:` — bug fix
  - `refactor:` — restructuring without behavior change
  - `docs:` — documentation only
  - `chore:` — tooling, config, dependencies, gitignore
- **Pre-commit gates**: Always run `security-audit` skill before committing
- **Do NOT commit**: `.env`, `credentials.json`, `token.json`, `*.tfstate`, `Zone.Identifier` files, `__pycache__/`, `.venv/`

### Branch Naming

All Claude-generated branches follow the pattern: `claude/<description>-<id>`

Example: `claude/update-claude-md-BGuLn`

### Creating Pull Requests

1. Run `security-audit` and `test-runner` on all changed code
2. Push to remote: `git push origin <branch-name>`
3. Create PR with `gh pr create` (includes test results and security scan in body)
4. Link related issues and add description context
5. Run `update-docs` skill after merge to sync documentation

## Tool Preference (Dedicated Tools > Bash)

Always use the right tool first — Bash is a fallback:

| Task | Preferred Tool | Bash Only When |
|------|---|---|
| Read a file | `Read` | File is too large (use offset/limit) |
| Edit a file | `Edit` | Bulk find-replace (use replace_all) |
| Create a file | `Write` | Creating a one-off script |
| Search files | `Grep` | Complex regex or multiple patterns |
| Find files | `Glob` | Pattern matching by name |
| Run processes | `Bash` | — (exclusive use case) |
| Git operations | `Bash` | — (exclusive use case) |
| System commands | `Bash` | — (exclusive use case) |

Reserve Bash for: running processes, git commands, system utilities, and anything the above tools cannot do.

## Bash Efficiency Rules

- Combine related sequential commands with `&&` in a single Bash call
- Use `;` only when earlier command failure is acceptable
- Avoid unnecessary `sleep` commands — use `run_in_background` for long tasks
- Never use interactive flags (`-i`) on git commands — not supported in this environment
- When invoking Python scripts from Bash, always use the full path: `.venv/bin/python` if venv exists

## Task Planning with TodoWrite

- For any task with 3 or more distinct steps, use `TodoWrite` to create a checklist before starting
- Mark items complete **as you finish them** — do not batch-complete at the end
- One active todo list per conversation; clear stale items when starting new work
- Update status in real-time, especially for long-running tasks

## Known Limitations & Workarounds

**Anthropic API connectivity**: Corporate network TLS handshake timeout (cached 2026-03-21)
- Workaround: Use mobile hotspot or VPN
- Detailed troubleshooting: `.claude/CONNECTIVITY-TROUBLESHOOTING.md`

**Data file locations**: Garmin JSON exports currently in `01-personal/aws-ai-agent/docs/`
- Target migration: `01-personal/garmin-health/data/raw/` on next pipeline run
- Use `data-pipeline` skill to orchestrate migration

## Resources

- **AWS**: [Bedrock](https://docs.aws.amazon.com/bedrock/), [Lambda](https://docs.aws.amazon.com/lambda/), [EventBridge](https://docs.aws.amazon.com/eventbridge/), [DynamoDB](https://docs.aws.amazon.com/dynamodb/)
- **Azure**: [AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- **Agent Frameworks**: [LangChain](https://python.langchain.com/), [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)
- **Local Dashboards**: [Streamlit](https://docs.streamlit.io/)
- **Terraform**: [Registry](https://registry.terraform.io/), [AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)

## Skill & Agent Registry

Full listing: `.claude/COMMAND_REGISTRY.md` (36 skills, 4 agents as of 2026-07-16, auto-loaded on startup)

Use short trigger phrases in conversation: "run tests", "terraform plan", "create issue", "update docs", etc.

For Cursor IDE: prefix with `/` (e.g., `/create-plan`, `/review`, `/test-runner`)
