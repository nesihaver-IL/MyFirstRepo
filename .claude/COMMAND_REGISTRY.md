# Command Registry
# Auto-generated list of available slash commands

## Available Commands

### Full Command Names
- create-issue
- exploration-phase
- create-plan
- execute-plan
- review
- peer-review
- update-docs
- azure-ai-foundry
- aws-strands
- aws-agentcore
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
| "dashboard" | analytics-metrics | Data visualization / Recharts charts |
| "chart" | analytics-metrics | KPI displays, metrics dashboards |
| "copilot" | copilot-docs | GitHub Copilot custom instructions |
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
```

### Direct Invocation (Claude Code)
```
Use the create-issue skill to log this bug

Use exploration-phase to understand this feature

Execute the create-plan skill
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

### Want Shorter Names?

Use trigger phrases instead:
- ✅ "explore this code"
- ✅ "create a plan"
- ✅ "review the code"

Instead of:
- ❌ `/exploration-phase`
- ❌ `/create-plan`
- ❌ `/review`

## Sync Commands

To update commands from repository:
```bash
# Pull latest commands
git pull origin claude/add-slash-commands-22qEL

# Restart your editor to reload
```

## Diagnostic Scripts

| Script | Purpose |
|--------|---------|
| `.claude/scripts/check-connectivity.sh` | Test internet, Anthropic API, CLI install, and auth |
| `.claude/scripts/check-connectivity.bat` | Same as above, for Windows |

Run before reporting login or connectivity issues.

## Command Status

Last Updated: 2026-02-26
Total Commands: 14
Status: ✅ Active
